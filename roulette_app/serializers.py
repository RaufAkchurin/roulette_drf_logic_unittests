from rest_framework import serializers

from roulette_app.models import SpinRound


class SpinListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpinRound
        fields = '__all__'
