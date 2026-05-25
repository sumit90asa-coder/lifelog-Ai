"""
Improved NLP parser — more sensitive mood scoring + better people filtering.
"""

import re
from textblob import TextBlob

# ── Activity keywords ────────────────────────────────────────
ACTIVITY_KEYWORDS = [
    'running','run','ran','jogging','jog','walking','walk','walked',
    'gym','workout','exercise','cycling','cycle','swimming','swim',
    'yoga','meditation','meditate','coding','programming','studying',
    'study','reading','read','writing','write','cooking','cook','cooked',
    'sleeping','sleep','slept','eating','hiking','hike','gaming','game',
    'drawing','painting','working','work','worked','travelling','travel',
    'shopping','shop','driving','drive','drove','singing','dancing','dance',
    'football','cricket','basketball','tennis','chess','music','playing','played',
]

# ── Words that look like names but aren't ────────────────────
FALSE_POSITIVE_NAMES = {
    'i','me','my','we','us','our','they','them','their','it','its',
    'the','a','an','is','was','are','were','be','been','being',
    'have','has','had','do','did','does','will','would','could','should',
    'then','also','but','and','or','so','yet','for','nor',
    # Tech / common words that start with capital
    'django','apis','api','rest','jwt','http','sql','css','html','json',
    'python','javascript','react','node','vue','aws','gcp','github',
    'monday','tuesday','wednesday','thursday','friday','saturday','sunday',
    'january','february','march','april','may','june','july','august',
    'september','october','november','december',
    'today','yesterday','morning','evening','afternoon','night',
}

# ── Emotion boosters/dampeners for better scoring ────────────
POSITIVE_BOOST = [
    'amazing','fantastic','excellent','great','awesome','wonderful',
    'happy','joyful','excited','love','loved','proud','productive',
    'motivated','inspired','brilliant','perfect','incredible','best',
]
NEGATIVE_BOOST = [
    'terrible','awful','horrible','worst','miserable','depressed',
    'anxious','stressed','exhausted','tired','sad','upset','angry',
    'frustrated','overwhelmed','lonely','failed','failure','hopeless',
]


def polarity_to_score(polarity: float, content: str) -> int:
    """
    Convert TextBlob polarity to 1–10 with keyword boosting.
    TextBlob tends to be conservative — we amplify it.
    """
    lower = content.lower()

    # Count boosters
    pos_hits = sum(1 for w in POSITIVE_BOOST if w in lower)
    neg_hits = sum(1 for w in NEGATIVE_BOOST if w in lower)

    # Boost polarity by keyword matches
    boosted = polarity + (pos_hits * 0.15) - (neg_hits * 0.15)
    boosted = max(-1.0, min(1.0, boosted))

    # Map -1→1, -0.5→3, 0→5, 0.5→7, 1→10 (non-linear for more spread)
    if boosted >= 0:
        score = 5 + round(boosted * 5)
    else:
        score = 5 + round(boosted * 4)

    return max(1, min(10, score))


def is_valid_person(word: str, position: int) -> bool:
    """Filter out false positives from people detection."""
    clean = re.sub(r'[^a-zA-Z]', '', word)
    if len(clean) < 2:                          return False
    if not clean[0].isupper():                  return False
    if clean.lower() in FALSE_POSITIVE_NAMES:   return False
    if position == 0:                           return False   # sentence start
    if re.match(r'^[A-Z]{2,}$', clean):         return False   # ALL CAPS = acronym
    if len(clean) > 15:                         return False   # too long
    return True


class EntryParser:

    @staticmethod
    def parse(content: str) -> dict:
        blob = TextBlob(content)

        polarity     = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        mood_score   = polarity_to_score(polarity, content)

        # ── People detection ─────────────────────────────────
        words  = content.split()
        people = []
        seen   = set()
        for i, word in enumerate(words):
            clean = re.sub(r'[^a-zA-Z]', '', word)
            if is_valid_person(clean, i) and clean not in seen:
                people.append(clean)
                seen.add(clean)

        # ── Activity detection ───────────────────────────────
        lower      = content.lower()
        activities = sorted({
            kw for kw in ACTIVITY_KEYWORDS
            if re.search(r'\b' + kw + r'\b', lower)
        })

        # ── Emotion label ─────────────────────────────────────
        if mood_score >= 9:     emotion = 'Very Happy'
        elif mood_score >= 7:   emotion = 'Happy'
        elif mood_score >= 5:   emotion = 'Neutral'
        elif mood_score >= 3:   emotion = 'Sad'
        else:                   emotion = 'Very Sad'

        return {
            'mood_score':       mood_score,
            'polarity':         round(polarity, 3),
            'subjectivity':     round(subjectivity, 3),
            'emotion':          emotion,
            'activities':       activities,
            'people_mentioned': people,
        }