from datetime import date, timedelta

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Entry, Streak
from .serializers import EntrySerializer, StreakSerializer
from .parser import EntryParser


AUTH = [JWTAuthentication, SessionAuthentication]


# ─────────────────────────────────────────────
# HELPER: calculate real consecutive-day streak
# ─────────────────────────────────────────────
def calculate_streak(user):
    # Get all unique dates the user made an entry (newest first)
    dates = (
        Entry.objects
        .filter(user=user)
        .values_list('created_at', flat=True)
        .order_by('-created_at')
    )

    if not dates:
        return 0

    # Collect unique calendar dates
    unique_days = sorted(
        set(d.date() if hasattr(d, 'date') else d for d in dates),
        reverse=True
    )

    today     = date.today()
    yesterday = today - timedelta(days=1)

    # Streak only counts if user wrote today OR yesterday
    if unique_days[0] < yesterday:
        return 0

    streak = 1
    for i in range(1, len(unique_days)):
        expected = unique_days[i - 1] - timedelta(days=1)
        if unique_days[i] == expected:
            streak += 1
        else:
            break

    return streak


# =========================================
# ENTRIES API
# =========================================

@api_view(['GET', 'POST'])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def entries(request):

    if request.method == 'GET':
        qs = Entry.objects.filter(user=request.user).order_by('-created_at')
        serializer = EntrySerializer(qs, many=True)
        return Response(serializer.data)

    # POST
    content = request.data.get('content', '')
    if not content.strip():
        return Response(
            {"error": "Content is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    parsed = EntryParser.parse(content)

    entry = Entry.objects.create(
        user=request.user,
        content=content,
        mood_score=parsed['mood_score']
    )

    return Response({
        "id":               entry.id,
        "content":          entry.content,
        "mood_score":       parsed['mood_score'],
        "activities":       parsed['activities'],
        "people_mentioned": parsed['people_mentioned'],
        "created_at":       entry.created_at,
    }, status=status.HTTP_201_CREATED)


# =========================================
# LIVE PREVIEW API
# =========================================

@api_view(['POST'])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def preview_entry(request):
    content = request.data.get('content', '')
    parsed  = EntryParser.parse(content)
    return Response(parsed)


# =========================================
# INSIGHTS API
# =========================================

@api_view(['GET'])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def insights(request):
    qs    = Entry.objects.filter(user=request.user)
    total = qs.count()

    if total:
        scores = [e.mood_score for e in qs if e.mood_score is not None]
        avg    = round(sum(scores) / len(scores), 1) if scores else 0
    else:
        avg = 0

    return Response({
        "total_entries":  total,
        "average_mood":   avg,
        "current_streak": calculate_streak(request.user),
    })


# =========================================
# STREAK API
# =========================================

@api_view(['GET'])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def streak_status(request):
    streak = calculate_streak(request.user)
    return Response({
        "current_streak": streak,
        "longest_streak": streak,
    })


# =========================================
# ENTRY DETAIL — DELETE + EDIT (PATCH)
# =========================================

@api_view(['GET', 'PATCH', 'DELETE'])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def entry_detail(request, pk):

    try:
        entry = Entry.objects.get(pk=pk, user=request.user)
    except Entry.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    # ─── GET ─────────────────────────────
    if request.method == 'GET':
        serializer = EntrySerializer(entry)
        return Response(serializer.data)

    # ─── PATCH (edit content) ────────────
    if request.method == 'PATCH':
        content = request.data.get('content', '').strip()
        if not content:
            return Response({"error": "Content required"}, status=status.HTTP_400_BAD_REQUEST)

        parsed = EntryParser.parse(content)
        entry.content    = content
        entry.mood_score = parsed['mood_score']
        entry.save()

        return Response({
            "id":         entry.id,
            "content":    entry.content,
            "mood_score": parsed['mood_score'],
            "created_at": entry.created_at,
        })

    # ─── DELETE ──────────────────────────
    if request.method == 'DELETE':
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =========================================
# AI INSIGHTS ENGINE
# =========================================

@api_view(['GET'])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def ai_insights(request):
    from .insights_engine import generate_insights
    insights_list = generate_insights(request.user)
    return Response({"insights": insights_list})


# =========================================
# ME — current user info
# =========================================

@api_view(['GET'])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response({
        "id":         user.id,
        "username":   user.username,
        "email":      user.email,
        "first_name": user.first_name,
        "last_name":  user.last_name,
        "full_name":  f"{user.first_name} {user.last_name}".strip() or user.username,
        "date_joined": user.date_joined,
    })