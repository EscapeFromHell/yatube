from http import HTTPStatus

from django.test import Client, TestCase

ABOUT = '/about/author/'
TECH = '/about/tech/'


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author(self):
        response = self.guest_client.get(ABOUT)
        self.assertTemplateUsed(response, 'about/author.html')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech(self):
        response = self.guest_client.get(TECH)
        self.assertTemplateUsed(response, 'about/tech.html')
        self.assertEqual(response.status_code, HTTPStatus.OK)
