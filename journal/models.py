from django.db import models
from django.contrib.auth.models import User


class Entry(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    content = models.TextField()

    mood_score = models.FloatField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.content[:50]


class Tag(models.Model):

    entry = models.ForeignKey(
        Entry,
        related_name='tags',
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)

    category = models.CharField(max_length=100)

    confidence = models.FloatField(default=0)

    def __str__(self):
        return self.name


class Metric(models.Model):

    entry = models.ForeignKey(
        Entry,
        related_name='metrics',
        on_delete=models.CASCADE
    )

    key = models.CharField(max_length=100)

    value = models.FloatField()

    unit = models.CharField(
        max_length=20,
        blank=True
    )

    def __str__(self):
        return self.key


class Streak(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    current_streak = models.IntegerField(
        default=0
    )

    longest_streak = models.IntegerField(
        default=0
    )

    def __str__(self):
        return self.user.username