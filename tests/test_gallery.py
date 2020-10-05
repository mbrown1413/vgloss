from django.test import TestCase, Client
from django.urls import reverse

from vgloss import models, scan
from tests import testdata

class TestScan(TestCase):

    def setUp(self):
        testdata.basic_data()
        scan.scan_all()

        self.client = Client()
        self.url = reverse("api-gallery")

    def tearDown(self):
        testdata.clean()

    def test_gallery_api(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, {
            "folders": ["dir1"],
            "tags": [],
        })

        tag1 = models.Tag.objects.create(name="tag1")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, {
            "folders": ["dir1"],
            "tags": [
                {"id": tag1.id, "name": "tag1", "parent": None},
            ],
        })
