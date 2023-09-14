from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
import random
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

        latest_spin = SpinRound.objects.filter(round=round).order_by("-last_step").first()
        round_last_step = latest_spin.last_step
        round_finished = SpinRound.objects.filter(round=round, finished=True).exists()

        if not round_finished:
            if round_last_step <= 9:
                new_spin = SpinRound.objects.create(
                    user=user,
                    round=round,
                    last_step=round_last_step + 1
                )
                serialized_data = SpinSerializer(new_spin).data
                get_random_from_array(new_spin, serialized_data)
                return Response(data=serialized_data, status=status.HTTP_200_OK)
                # TODO записать в логи наше число и номер степа

            if round_last_step == 10:
                latest_spin.finished = True
                latest_spin.save()
                latest_spin.refresh_from_db()

                serialized_data = SpinSerializer(latest_spin).data
                serialized_data.update({"num": 777})
                return Response(data=serialized_data, status=status.HTTP_200_OK)

        if round_finished:
            raise ValidationError("Sorry, this round finished")

        else:
            raise ValidationError("Unknown mistake in server")


def get_random_from_array(spin: SpinRound, serialized_data: dict) -> dict:
    numbers = spin.rest_values.split(",")
    random_num = random.choice(numbers)
    numbers.remove(random_num)
    serialized_data.update({"num": int(random_num)})
    return serialized_data
