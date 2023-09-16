from rest_framework import serializers

from roulette_app.models import SpinRound


class StatisticSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpinRound
        fields = "__all__"


class SpinSerializer(serializers.ModelSerializer):
    last_step = serializers.IntegerField(required=False)

    class Meta:
        model = SpinRound
        fields = (
            "user",
            "round",
            "last_step",
        )
