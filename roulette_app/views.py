from typing import Tuple, Optional

from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
import random
from rest_framework.views import APIView

from roulette_app.models import Spin, User, Round
from roulette_app.serializers import SpinSerializer


class StatisticView(APIView):
    def get(self, request, *args, **kwargs):
        if Spin.objects.exists():
            rounds = Spin.objects.values("round").distinct()
            rounds_list = [item['round'] for item in rounds if 'round' in item]

            rounds_statistic = {}
            for round in rounds_list:
                users_in_round = Spin.objects.filter(round=round).values("user_id").distinct().count()
                rounds_statistic.update({round: users_in_round})

            active_users = {}
            spin_all = Spin.objects.all()
            users_all = User.objects.all()

            count = 0
            for user in users_all:
                distinct_rounds = spin_all.filter(user=user.id).values("round").distinct()
                if distinct_rounds.count():
                    count += 1
                    total_spin = spin_all.filter(user=user.id).count()
                    active_users.update({
                        f"{count}":
                            {
                                "id": user.pk,
                                "rounds_count": distinct_rounds.count(),
                                "spin_per_round": total_spin / distinct_rounds.count(),
                                "total_spin_optional": total_spin,
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
        user_id = request.data.get("user")
        user = User.objects.filter(id=user_id).last()

        #  Проверка наличия первого раунда
        if not Round.objects.exists():
            round_new = Round.objects.create()
            num = get_random_from_dict_with_weith(round_new)
            new_spin = Spin.objects.create(
                user=user,
                round=round_new,
            )
            #  logging number
            round_new.numbers.update({num: user.id})
            round_new.save()
            round_new.refresh_from_db()

            #  response generation
            serialized_data = SpinSerializer(new_spin).data
            serialized_data.update({"num": num})
            return Response(data=serialized_data, status=status.HTTP_200_OK)

        else:

            # last_round_db = Spin.objects.order_by("round").last().round
            # if int(round) < int(last_round_db):
            #     raise ValidationError("Sorry you round is not latest")

            latest_spin = Spin.objects.last()
            round_actual = Round.objects.last()
            round_last_step = len(round_actual.numbers.items())

            if not round_actual.finished:
                if round_last_step <= 9:
                    num = get_random_from_dict_with_weith(round_actual)
                    new_spin = Spin.objects.create(
                        user=user,
                        round=round_actual,
                    )
                    #  logging number
                    round_actual.numbers.update({num: user.id})
                    round_actual.save()
                    round_actual.refresh_from_db()

                    #  response generation
                    serialized_data = SpinSerializer(new_spin).data
                    serialized_data.update({"num": num})
                    return Response(data=serialized_data, status=status.HTTP_200_OK)

            if round_last_step == 10:  # Jackpot
                latest_spin.finished = True
                latest_spin.save()
                latest_spin.refresh_from_db()

                serialized_data = SpinSerializer(latest_spin).data
                serialized_data.update({"num": 777, "finished": True})
                return Response(data=serialized_data, status=status.HTTP_200_OK)

            # TODO test this please
            else:
                try:
                    num = get_random_from_dict_with_weith(round_actual)
                    round_new = Round.objects.create()
                    new_spin = Spin.objects.create(
                        user=user,
                        round=round_new,
                    )

                    #  logging number
                    round_new.numbers.update({num: user.id})
                    round_new.save()
                    round_new.refresh_from_db()

                    #  response generation
                    serialized_data = SpinSerializer(new_spin).data
                    serialized_data.update({"num": num})
                    return Response(data=serialized_data, status=status.HTTP_200_OK)
                except:
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


# TODO только самые бооольшие 3 значения в статистике сделать
# TODO отрефакторить убрать из модели рест вэлью по умолчанию
# TODO отрефакторить гет номер чтобы без стринги работало

# TODO отрефакторить респонсы в отельный метод попытаться вынести
# TODO перепроверить работу весов
# TODO упаковать в докер

