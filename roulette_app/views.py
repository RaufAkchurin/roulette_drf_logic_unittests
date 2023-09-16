from typing import Tuple, Optional
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
import random

from rest_framework.views import APIView

from roulette_app.models import SpinRound, User
from roulette_app.serializers import SpinSerializer


# TODO доработать уникальность выпадающих значений
# TODO тест на уникальность значений

class StatisticView(APIView):
    def get(self, request, *args, **kwargs):
        if SpinRound.objects.exists():
            rounds = SpinRound.objects.values("round").distinct()
            rounds_list = [item['round'] for item in rounds if 'round' in item]

            # total_steps = queryset.aggregate(total_steps=Sum('last_step'))['total_steps']
            # avg_steps_per_round = total_steps / total_rounds if total_rounds else 0

            rounds_statistic = {}
            for round in rounds_list:
                users_in_round = SpinRound.objects.filter(round=round).values("user_id").count()
                rounds_statistic.update({round: users_in_round})

            # most_active_users = SpinRound.objects.

            response_data = {
                "rounds_statistic": rounds_statistic
            }

            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        else:
            return Response({'detail': 'Statistic is empty, try to play'}, status=status.HTTP_204_NO_CONTENT)


class SpinView(viewsets.ModelViewSet):
    queryset = SpinRound.objects.all()
    serializer_class = SpinSerializer

    # TODO тесты ендпоинт статистики
    # TODO сделаеть ендпоинт статистики
    # TODO отрефакторить убрать из модели рест вэлью по умолчанию
    # TODO отрефакторить гет номер чтобы без стринги работало
    # TODO отрефакторить респонсы в отельный метод попытаться вынести
    # TODO внедрить весы
    # TODO упаковать в докер

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user")
        user = User.objects.filter(id=user_id).last()

        #  Проверка наличия первого раунда
        if not SpinRound.objects.exists():
            num, rest_values = get_random_from_array(start_round=True)
            new_spin = SpinRound.objects.create(
                user=user,
                rest_values=rest_values,
            )
            serialized_data = SpinSerializer(new_spin).data
            serialized_data.update({"num": num})
            return Response(data=serialized_data, status=status.HTTP_200_OK)

        round = request.data.get("round")

        # last round checker:
        last_round_db = SpinRound.objects.order_by("round").last().round
        if int(round) < int(last_round_db):
            raise ValidationError("Sorry you round is not latest")

        latest_spin = SpinRound.objects.filter(round=round).order_by("-last_step").first()
        round_last_step = latest_spin.last_step
        round_finished = SpinRound.objects.filter(round=round, finished=True).exists()

        if not round_finished:
            if round_last_step <= 9:
                num, rest_values = get_random_from_array(latest_spin.rest_values)
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
            num, rest_values = get_random_from_array(start_round=True)
            new_spin = SpinRound.objects.create(
                user=user,
                round=int(round) + 1,
                rest_values=rest_values
            )
            serialized_data = SpinSerializer(new_spin).data
            serialized_data.update({"num": num})
            return Response(data=serialized_data, status=status.HTTP_200_OK)
        else:
            raise ValidationError("Unknown mistake in server")


def get_random_from_array(start_round: bool = False, rest_values: Optional[str] = None) -> Tuple[int, str]:
    if start_round:
        rest_values = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    else:
        rest_values = rest_values.split(",")
    random_num = random.choice(rest_values)
    rest_values.remove(random_num)
    return int(random_num), ",".join(rest_values)
