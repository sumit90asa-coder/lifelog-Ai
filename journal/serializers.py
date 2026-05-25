from rest_framework import serializers

from .models import Entry
from .models import Tag
from .models import Metric
from .models import Streak


class TagSerializer(serializers.ModelSerializer):

    class Meta:

        model = Tag

        fields = '__all__'


class MetricSerializer(serializers.ModelSerializer):

    class Meta:

        model = Metric

        fields = '__all__'


class EntrySerializer(serializers.ModelSerializer):

    tags = TagSerializer(
        many=True,
        read_only=True
    )

    metrics = MetricSerializer(
        many=True,
        read_only=True
    )

    class Meta:

        model = Entry

        fields = '__all__'


class StreakSerializer(serializers.ModelSerializer):

    class Meta:

        model = Streak

        fields = '__all__'