import unittest

from django.test import TestCase, Client
from django.urls import reverse

from vgloss import models, scan
from tests import testdata

class TestScan(TestCase):

    def setUp(self):
        testdata.basic_data()
        scan.scan_all()

        # Tag some files
        self.tag_white = models.Tag.objects.create(name="white")
        self.tag_black = models.Tag.objects.create(name="black")
        white_square = models.File.objects.get(name="white_square.jpg")
        black_square = models.File.objects.get(name="black_square1.jpg")
        models.FileTag.objects.create(tag=self.tag_white, file=white_square)
        models.FileTag.objects.create(tag=self.tag_black, file=black_square)

        self.client = Client()
        self.url = reverse("api-files")

    def tearDown(self):
        testdata.clean()

    def test_file_list(self):
        # List root folder
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(
            set(f["name"] for f in response.data),
            {
                "black_square1.jpg",
                "white_square.jpg",
                "not_image.txt",
            }
        )

        # Listing should return tag in data
        self.assertSetEqual(
            set((f["name"], str(f["tags"])) for f in response.data),
            {
                ("black_square1.jpg", str([self.tag_black.id])),
                ("white_square.jpg", str([self.tag_white.id])),
                ("not_image.txt", str([])),
            }
        )

        # List sub-folder
        for dirname in ["/dir1/", "dir1/", "dir1", "/dir1"]:
            response = self.client.get(self.url+"?folder="+dirname)
            self.assertEqual(response.status_code, 200)
            self.assertSetEqual(
                set(f["name"] for f in response.data),
                {"black_square1.jpg"}
            )

    @unittest.skip("Test not implemented")
    def test_file_list_filtered(self):

        # Filter files by tag
        response = self.client.get(self.url+"?tag="+str(self.tag_white.id))
        self.assertEqual(response.status_code, 200)
        raise NotImplementedError

        # List files by both tag and folder
        raise NotImplementedError

    @unittest.skip("Test not implemented")
    def test_file_detail(self):
        raise NotImplementedError
