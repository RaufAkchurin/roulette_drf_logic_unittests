
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse


# Create your tests here.


class SpinTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("v1:spin")

    def test_url(self):
        self.assertEqual(self.url, "/v1/spin")
