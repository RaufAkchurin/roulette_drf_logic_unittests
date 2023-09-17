from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from roulette_app.models import SpinRound


# Create your tests here.


class SpinTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("v1:spin")
        self.user_one = User.objects.create(username="user_one")

    def test_url(self):
        self.assertEqual(self.url, "/v1/spin")

    def test_spin(self):
        # TODO remove this after wrote first checker logic
        SpinRound.objects.create(user=self.user_one, round=1)

        response = self.client.post(data={"user": self.user_one.pk, "round": 1}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["round"], 1)
        self.assertEqual(response.data["user"], 1)
        self.assertEqual(response.data["last_step"], 2)

    def test_jackpot_after_10th_spin(self):
        SpinRound.objects.create(user=self.user_one, round=1, last_step=10)
        response = self.client.post(data={"user": self.user_one.pk, "round": 1}, path=self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["num"], 777)
        self.assertEqual(response.data["finished"], True)

    def test_auto_create_new_round_after_finished(self):
        SpinRound.objects.create(user=self.user_one, round=1, finished=True)
        response = self.client.post(data={"user": self.user_one.pk, "round": 1}, path=self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["round"], 2)
        self.assertEqual(response.data["last_step"], 1)

    def test_create_first_spin_in_db(self):
        response = self.client.post(data={"user": self.user_one.pk, "round": 1}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_empty_user(self):
        response = self.client.post(data={"round": 1}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_user(self):
        response = self.client.post(data={"user": [1, 2, 3], "round": 1}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_without_round(self):
        response = self.client.post(data={"user": self.user_one.pk}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class StatisticTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("v1:statistic")
        self.user_one = User.objects.create(username="user_one")
        self.user_two = User.objects.create(username="user_two")
        self.user_three = User.objects.create(username="user_three")

    def test_url(self):
        self.assertEqual(self.url, "/v1/statistic")

    def test_simple(self):
        # 1 round  # user_one - 5
        for i in range(5):
            SpinRound.objects.create(round=1, last_step=i, user=self.user_one)
        #     # user_two - 3
        # for i in range(6, 9):
        #     SpinRound.objects.create(round=1, last_step=i, user=self.user_two)
        #
        # # 2 round # user_one - 3
        #
        # for i in range(3):
        #     SpinRound.objects.create(round=2, last_step=i, user=self.user_one)
        #     # user_two - 1
        # for i in range(4, 5):
        #     SpinRound.objects.create(round=2, last_step=i, user=self.user_two)

        # 3 round # user_three - 7

        # for i in range(7):
        #     SpinRound.objects.create(round=3, last_step=i, user=self.user_three)
        #
        response = (self.client.get(path=self.url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # rounds_statistic_expected = {1: 8, 2: 4, 3: 7}
        # self.assertEqual(response.data["rounds_statistic"], rounds_statistic_expected)

        active_users_expected = {
            "1": {
                "id": 3,
                "rounds_count": 8,
                "total_spin": 7
            },
            # "2": {
            #     "id": 2,
            #     "rounds_count": 3,
            #     "spin_avg": 0.6666666666666666
            # },
            # "3": {
            #     "id": 3,
            #     "rounds_count": 9,
            #     "spin_avg": 0.3333333333333333
            # }
        }
        self.assertEqual(response.data["active_users"], active_users_expected)
