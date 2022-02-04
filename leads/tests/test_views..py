from django.test import TestCase
from django.shortcuts import reverse

class LandingPageTest(TestCase):

    def test_status_code(self):
        res = self.client.get(reverse("landing_page"))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "landing.html")
        