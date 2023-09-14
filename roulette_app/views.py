from typing import Tuple
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
import random
from roulette_app.models import SpinRound
from roulette_app.serializers import RoundListSerializer, SpinSerializer


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

        # TODO тестами покрыть
        # TODO убрать ласт степ из объязательных параметров запроса
        # TODO избавиться от 500 если были значения

        if not round_finished:
            if round_last_step <= 9:
                num, rest_values = get_random_from_array(latest_spin)
                new_spin = SpinRound.objects.create(
                    user=user,
                    round=round,
                    last_step=round_last_step + 1,
                    rest_values=rest_values
                )
                serialized_data = SpinSerializer(new_spin).data
                serialized_data.update({"num": num})
                return Response(data=serialized_data, status=status.HTTP_200_OK)
                # TODO записать в логи наше число и номер степа

            if round_last_step == 10:  # Jackpot
                latest_spin.finished = True
                latest_spin.save()
                latest_spin.refresh_from_db()

                serialized_data = SpinSerializer(latest_spin).data
                serialized_data.update({"num": 777, "finished": True})
                return Response(data=serialized_data, status=status.HTTP_200_OK)

        if round_finished:
            new_spin = SpinRound.objects.create(
                user=user,
                round=round + 1,
                last_step=1
            )
            serialized_data = SpinSerializer(new_spin).data
            return Response(data=serialized_data, status=status.HTTP_200_OK)
        else:
            raise ValidationError("Unknown mistake in server")


def get_random_from_array(spin: SpinRound) -> Tuple[int, str]:
    rest_values = spin.rest_values.split(",")
    random_num = random.choice(rest_values)
    rest_values.remove(random_num)
    return int(random_num), ",".join(rest_values)

