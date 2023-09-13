from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.response import Response

from roulette_app.models import SpinRound
from roulette_app.serializers import RoundListSerializer, SpinSerializer


# Create your views here.

class RoundsListViewSet(viewsets.ModelViewSet):
    queryset = SpinRound.objects.all()
    serializer_class = RoundListSerializer


class SpinView(viewsets.ModelViewSet):
    queryset = SpinRound.objects.all()
    serializer_class = SpinSerializer

    def create(self, request, *args, **kwargs):
        user = request.data.get("user")
        round = request.data.get("round")

        round_last_step = SpinRound.objects.filter(round=round).order_by("-last_step").first().last_step
        if round_last_step <= 9:
            SpinRound.objects.create(
                user=user,
                round=round,
                last_step=round_last_step + 1
            )
        elif round_last_step == 10:
            # TODO jackpot
            pass
        # data = SpinSerializer(spin_instance).data
        return Response(data=round_last_step, status=status.HTTP_200_OK)
