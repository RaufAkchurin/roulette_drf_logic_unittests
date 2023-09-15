import unittest

from rest_framework.reverse import reverse


# Create your tests here.


class SpinTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.url = reverse("api:spin")

    def test_url(self):
        self.assertEqual(self.url, "/api/spin/")
