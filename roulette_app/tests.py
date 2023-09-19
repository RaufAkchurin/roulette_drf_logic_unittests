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
        self.user_two = User.objects.create(username="user_two")
        self.round_one = Round.objects.create()

    def test_url(self):
        self.assertEqual(self.url, "/v1/spin")

    def test_creating_first_round(self):
        self.round_one.delete()
        response = self.client.post(data={"user": self.user_one.pk, "round": 2}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["round"], 2)  # because first is deleted
        self.assertEqual(response.data["user"], 1)

        # check logging first num
        round_from_db = Round.objects.last()
        self.assertEqual(len(round_from_db.numbers), 1)

        # check logging second num
        response = self.client.post(data={"user": self.user_two.pk, "round": 1}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["round"], 2)  # because first is deleted
        self.assertEqual(response.data["user"], 2)

        round_from_db = Round.objects.last()
        self.assertEqual(len(round_from_db.numbers), 2)

    def test_unique_numbers(self):
        for i in range(10):
            self.client.post(data={"user": self.user_two.pk, "round": 1}, path=self.url)

        round_from_db = Round.objects.last()
        numbers = set(round_from_db.numbers.keys())
        self.assertEqual(len(numbers), 10)

    def test_spin(self):
        response = self.client.post(data={"user": self.user_one.pk, "round": self.round_one.pk}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["round"], 1)
        self.assertEqual(response.data["user"], 1)

    def test_jackpot_after_10th_spin(self):
        full_round = Round.objects.create(
            numbers={1: 20, 2: 100, 3: 45, 4: 70, 5: 15, 6: 140, 7: 20, 8: 20, 9: 140, 10: 45})
        Spin.objects.create(user=self.user_one, round=full_round)
        response = self.client.post(data={"user": self.user_one.pk, "round": full_round.id}, path=self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["num"], 777)
        self.assertEqual(response.data["finished"], True)

    def test_creating_new_after_finish(self):
        finished_round = Round.objects.create(finished=True)
        response = self.client.post(data={"user": self.user_one.pk, "round": finished_round.id}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["round"], finished_round.id + 1)

        # check logging first num
        round_from_db = Round.objects.last()
        self.assertEqual(len(round_from_db.numbers), 1)

    def test_without_round(self):
        response = self.client.post(data={"user": self.user_one.pk}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_without_user(self):
        response = self.client.post(data={"round": self.round_one.pk}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0], "This user not correct")

    def test_user_validation(self):
        response = self.client.post(data={"round": self.round_one.pk, "user": [1, 2, 3]}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0], "This user not correct")


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
