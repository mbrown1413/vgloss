from django.test import TestCase, Client

from vgloss import models, scan
from tests import testdata

class TestGallery(TestCase):

    def setUp(self):
        testdata.basic_data()
        scan.scan_all()

        self.client = Client()

    def tearDown(self):
        testdata.clean()

    def test_gallery_initial_data(self):
        """Page should include initial metadata."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.context["metadata"], {
            "folders": ["dir1"],
            "tags": [],
        })

        tag1 = models.Tag.objects.create(name="tag1")

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.context["metadata"], {
            "folders": ["dir1"],
            "tags": [
                {"id": tag1.id, "name": "tag1", "parent": None},
            ],
        })
