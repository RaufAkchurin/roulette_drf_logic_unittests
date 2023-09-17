from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from roulette_app.models import Spin, Round


# Create your tests here.


class SpinTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("v1:spin")
        self.user_one = User.objects.create(username="user_one")
        self.round_one = Round.objects.create()

    def test_url(self):
        self.assertEqual(self.url, "/v1/spin")

    def test_spin(self):
        response = self.client.post(data={"user": self.user_one.pk, "round": self.round_one.pk}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["round"], 1)
        self.assertEqual(response.data["user"], 1)

    def test_check_deleting_from_rest_values(self):
        round_new = Round.objects.create(numbers={5: self.user_one.pk})

        response = self.client.post(data={"user": self.user_one.pk, "round": round_new.pk}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["round"], 1)
        self.assertEqual(response.data["user"], 1)

    def test_jackpot_after_10th_spin(self):
        Spin.objects.create(user=self.user_one, round=self.round_one)
        response = self.client.post(data={"user": self.user_one.pk, "round": self.round_one.id}, path=self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["num"], 777)
        self.assertEqual(response.data["finished"], True)

    def test_auto_create_new_round_after_finished(self):
        Spin.objects.create(user=self.user_one, round=self.round_one, finished=True)
        response = self.client.post(data={"user": self.user_one.pk, "round": self.round_one.pk}, path=self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["round"], 2)

    def test_create_first_spin_in_db(self):
        response = self.client.post(data={"user": self.user_one.pk, "round": self.round_one.id}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_empty_user(self):
        response = self.client.post(data={"round": self.round_one.id}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_user(self):
        response = self.client.post(data={"user": [1, 2, 3], "round": self.round_one.id}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_without_round(self):
        response = self.client.post(data={"user": self.user_one.pk}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class StatisticTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("v1:statistic")
        self.round_one = Round.objects.create(id=1)
        self.round_two = Round.objects.create(id=2)
        self.round_three = Round.objects.create(id=3)
        self.round_four = Round.objects.create(id=4)
        self.round_five = Round.objects.create(id=5)
        self.round_six = Round.objects.create(id=6)
        self.round_seven = Round.objects.create(id=7)
        self.round_eight = Round.objects.create(id=8)

        self.user_one = User.objects.create(username="user_one")
        self.user_two = User.objects.create(username="user_two")
        self.user_three = User.objects.create(username="user_three")
        self.user_four = User.objects.create(username="user_four")  # without rounds
        self.user_five = User.objects.create(username="user_five")

    def test_url(self):
        self.assertEqual(self.url, "/v1/statistic")

    def test_simple(self):
        # 1 user
        for i in range(3):
            Spin.objects.create(round=self.round_one, user=self.user_one)

        # 2 user

        for i in range(5):
            Spin.objects.create(round=self.round_two, user=self.user_two)
        for i in range(7):
            Spin.objects.create(round=self.round_three, user=self.user_two)

        # 3 user
        for i in range(4):
            Spin.objects.create(round=self.round_four, user=self.user_three)
        for i in range(5):
            Spin.objects.create(round=self.round_five, user=self.user_three)

        # 5 user
        for i in range(4):
            Spin.objects.create(round=self.round_six, user=self.user_five)
        for i in range(5):
            Spin.objects.create(round=self.round_seven, user=self.user_five)

        response = (self.client.get(path=self.url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rounds_statistic_expected = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1}
        self.assertEqual(response.data["rounds_statistic"], rounds_statistic_expected)

        active_users_expected = {
            '2': {'id': 2,
                  'rounds_count': 2,
                  'spin_per_round': 6.0,
                  'total_spin_optional': 12},
            '3': {'id': 3,
                  'rounds_count': 2,
                  'spin_per_round': 4.5,
                  'total_spin_optional': 9},
            '4': {'id': 5,
                  'rounds_count': 2,
                  'spin_per_round': 4.5,
                  'total_spin_optional': 9}}

        self.assertEqual(response.data["active_users"], active_users_expected)
