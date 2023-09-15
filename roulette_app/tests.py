from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from roulette_app.models import SpinRound


# Create your tests here.


class SpinTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("v1:spin")

    def test_url(self):
        self.assertEqual(self.url, "/v1/spin")

    def test_spin(self):
        # TODO remove this after wrote first checker logic
        SpinRound.objects.create(user='user', round=1)

        response = self.client.post(data={"user": 'user', "round": 1}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["round"], 1)
        self.assertEqual(response.data["user"], 'user')
        self.assertEqual(response.data["last_step"], 2)

        #  check num is removed from rest_values
        last_spin = SpinRound.objects.all().order_by("created_at").last()
        self.assertEqual(len(last_spin.rest_values.split(",")), 8)

    def test_jackpot_after_10th_spin(self):
        SpinRound.objects.create(user='user', round=1, last_step=10)
        response = self.client.post(data={"user": 'user', "round": 1}, path=self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["num"], 777)
        self.assertEqual(response.data["finished"], True)

    def test_auto_create_new_round_after_finished(self):
        SpinRound.objects.create(user='user', round=1, finished=True)
        response = self.client.post(data={"user": 'user', "round": 1}, path=self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["round"], 2)
        self.assertEqual(response.data["last_step"], 1)

    def test_irrelevant_round(self):
        SpinRound.objects.create(user='user', round=1, finished=True)
        response = self.client.post(data={"user": 'user', "round": 1}, path=self.url)

        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, "123")

    # TODO why not work???
    def create_first_spin_in_db(self):
        SpinRound.objects.create(user='user', round=1)
        response = self.client.post(data={"user": 'user', "round": 1}, path=self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
