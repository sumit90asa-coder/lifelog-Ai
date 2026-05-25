"""
AI Insights Engine — generates human-readable insights from journal patterns.
Add to api.py: from .insights_engine import generate_insights
"""

from collections import Counter
from datetime import date, timedelta
from .models import Entry


def generate_insights(user):
    entries = list(
        Entry.objects.filter(user=user).order_by('-created_at')[:50]
    )

    if not entries:
        return ["Start journaling to unlock AI insights!"]

    insights = []

    # ── 1. Best mood day of week ──────────────────────────────
    day_moods = {}
    for e in entries:
        day = e.created_at.strftime('%A')
        day_moods.setdefault(day, []).append(e.mood_score)

    if day_moods:
        best_day = max(day_moods, key=lambda d: sum(day_moods[d]) / len(day_moods[d]))
        insights.append(f"📅 You feel happiest on {best_day}s.")

    # ── 2. Mood trend (last 7 vs previous 7) ─────────────────
    if len(entries) >= 7:
        recent_avg = sum(e.mood_score for e in entries[:7]) / 7
        if len(entries) >= 14:
            prev_avg = sum(e.mood_score for e in entries[7:14]) / 7
            diff = recent_avg - prev_avg
            if diff > 0.5:
                insights.append(f"📈 Your mood improved by {diff:.1f} points this week!")
            elif diff < -0.5:
                insights.append(f"📉 Your mood dipped {abs(diff):.1f} points. Keep going!")
            else:
                insights.append("➡️ Your mood has been consistent this week.")

    # ── 3. Most common mood score ─────────────────────────────
    mood_counts = Counter(e.mood_score for e in entries)
    common_mood = mood_counts.most_common(1)[0][0]
    insights.append(f"💡 Your most frequent mood score is {common_mood}/10.")

    # ── 4. Activity impact ───────────────────────────────────
    from .parser import EntryParser
    activity_moods = {}
    for e in entries:
        parsed = EntryParser.parse(e.content)
        for act in parsed.get('activities', []):
            activity_moods.setdefault(act, []).append(e.mood_score)

    if activity_moods:
        best_act = max(activity_moods, key=lambda a: sum(activity_moods[a]) / len(activity_moods[a]))
        best_score = sum(activity_moods[best_act]) / len(activity_moods[best_act])
        insights.append(f"🏃 You feel best ({best_score:.1f}/10) when you {best_act}.")

    # ── 5. Journaling consistency ─────────────────────────────
    unique_days = set(e.created_at.date() for e in entries)
    total_days  = (date.today() - min(unique_days)).days + 1
    consistency = round(len(unique_days) / total_days * 100)
    insights.append(f"📓 You've journaled on {consistency}% of days since you started.")

    # ── 6. High vs low mood entries ──────────────────────────
    high = [e for e in entries if e.mood_score >= 8]
    low  = [e for e in entries if e.mood_score <= 3]
    if high:
        insights.append(f"✨ You've had {len(high)} great day(s) — keep doing what works!")
    if low:
        insights.append(f"💙 You've had {len(low)} tough day(s). You pushed through each one.")

    return insights