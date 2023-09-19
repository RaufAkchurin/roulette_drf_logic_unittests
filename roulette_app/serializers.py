from django.contrib.auth.models import User
from rest_framework import serializers

from roulette_app.models import Spin


class StatisticSerializer(serializers.ModelSerializer):

    class Meta:
        model = Spin
        fields = "__all__"


class SpinSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        allow_null=False,
        required=True
    )
    last_step = serializers.IntegerField(required=False)

    class Meta:
        model = Spin
        fields = "__all__"

    def validate_user(self, value):
        if not value:
            raise serializers.ValidationError("User field cant be empty")
        return value
