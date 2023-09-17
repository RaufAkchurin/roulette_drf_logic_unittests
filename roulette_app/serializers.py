from rest_framework import serializers

from roulette_app.models import Spin


class StatisticSerializer(serializers.ModelSerializer):

    class Meta:
        model = Spin
        fields = "__all__"


class SpinSerializer(serializers.ModelSerializer):
    last_step = serializers.IntegerField(required=False)

    class Meta:
        model = Spin
        fields = (
            "user",
            "round",
            "last_step",
        )
