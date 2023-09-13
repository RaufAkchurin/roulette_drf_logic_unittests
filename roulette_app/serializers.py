from rest_framework import serializers

from roulette_project.roulette_app.models import SpinRound


class SpinSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpinRound
        fields = '__all__'
