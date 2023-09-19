from typing import Tuple, Optional

from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
import random
from rest_framework.views import APIView

from roulette_app.models import Spin, User, Round
from roulette_app.serializers import SpinSerializer


class StatisticView(APIView):
    def get(self, request, *args, **kwargs):
        if Round.objects.exists():
            rounds_statistic = {}
            rounds = Round.objects.annotate()
            for round in rounds:
                users = len(set(round.numbers.values()))
                rounds_statistic.update({round.pk: users})

            active_users = {}
            users_with_spin = User.objects.annotate(spins_count=Count('user_spins'))

            count = 0
            for user in users_with_spin.order_by("-spins_count")[:3]:
                distinct_rounds = Spin.objects.filter(user=user.id).values("round").distinct()
                if distinct_rounds.count():
                    count += 1
                    active_users.update({
                        f"{count}":
                            {
                                "id": user.pk,
                                "rounds_count": distinct_rounds.count(),
                                "spin_per_round": user.spins_count / distinct_rounds.count(),
                                "total_spin_optional": user.spins_count,
                            }}
                    )



                response_data = {
                    "rounds_statistic": rounds_statistic,
                    "active_users": active_users
                }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Statistic is empty, try to play'}, status=status.HTTP_204_NO_CONTENT)


class SpinView(viewsets.ModelViewSet):
    queryset = Spin.objects.all()
    serializer_class = SpinSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user", None)

        user = User.objects.filter(id=user_id).last()
        if user is None:
            raise ValidationError("This user not correct")

        round_actual = Round.objects.last()

        #  Проверка наличия первого раунда
        if not Round.objects.exists() or round_actual.finished:
            round_new = Round.objects.create()
            num = get_random_from_dict_with_weith(round_new)
            new_spin = Spin.objects.create(
                user=user,
                round=round_new,
            )
            round_new.logging(round_new, num, user)

            #  response generation
            serialized_data = SpinSerializer(new_spin).data
            serialized_data.update({"num": num})
            return Response(data=serialized_data, status=status.HTTP_200_OK)

        else:

            latest_spin = Spin.objects.last()
            round_last_step = len(round_actual.numbers.items())

            if not round_actual.finished:
                if round_last_step <= 9:
                    num = get_random_from_dict_with_weith(round_actual)
                    new_spin = Spin.objects.create(
                        user=user,
                        round=round_actual,
                    )
                    round_actual.logging(round_actual, num, user)

                    #  response generation
                    serialized_data = SpinSerializer(new_spin).data
                    serialized_data.update({"num": num})
                    return Response(data=serialized_data, status=status.HTTP_200_OK)

            if round_last_step == 10:  # Jackpot
                round_actual.finished = True
                round_actual.save()
                round_actual.refresh_from_db()

                round_actual.logging(round_actual, 777, user)

                serialized_data = SpinSerializer(latest_spin).data
                serialized_data.update({"num": 777, "finished": True})
                return Response(data=serialized_data, status=status.HTTP_200_OK)

            else:
                raise ValidationError("Unknown mistake in server")


def get_random_from_dict_with_weith(round: Round):
    defaul_values = {1: 20, 2: 100, 3: 45, 4: 70, 5: 15, 6: 140, 7: 20, 8: 20, 9: 140, 10: 45}
    if len(round.numbers) == 0:
        rest_values = {1: 20, 2: 100, 3: 45, 4: 70, 5: 15, 6: 140, 7: 20, 8: 20, 9: 140, 10: 45}

    else:
        for number in round.numbers:
            defaul_values.pop(int(number), None)
        rest_values = defaul_values
    # Сумма всех вероятностей
    total_prob = sum(rest_values.values())
    # Генерация случайного числа в диапазоне от 1 до суммы вероятностей
    rand_num = random.randint(1, total_prob)
    # Перебор ключей и вычитание вероятности каждого ключа
    for key, prob in rest_values.items():
        rand_num -= prob
        if rand_num <= 0:
            return key

# TODO отрефакторить респонсы в отельный метод попытаться вынести
# TODO перепроверить работу весов
# TODO упаковать в докер
