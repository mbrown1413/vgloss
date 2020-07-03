from django.test import TestCase, Client
from django.urls import reverse

from vgloss import models

class TestFileTag(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("api-file-tags")

        self.tag1 = models.Tag.objects.create(name="tag1")
        self.tag2 = models.Tag.objects.create(name="tag2")
        self.file1 = models.File.objects.create(hash="hash1", name="file1",
                                                mimetype="image/png")
        self.file2 = models.File.objects.create(hash="hash2", name="file2",
                                                mimetype="image/png")

    def test_create(self):
        response = self.client.post(self.url, [{
            "file": self.file1.hash,
            "tag": self.tag1.id,
        }], content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(models.FileTag.objects.values("file_id", "tag_id")),
            [{"file_id": "hash1", "tag_id": self.tag1.id}],
        )

    def test_delete(self):
        models.FileTag.objects.create(file_id=self.file1.hash, tag_id=self.tag1.id)
        models.FileTag.objects.create(file_id=self.file1.hash, tag_id=self.tag2.id)
        models.FileTag.objects.create(file_id=self.file2.hash, tag_id=self.tag1.id)
        self.assertEqual(models.FileTag.objects.count(), 3)
        response = self.client.delete(self.url, [{
            "file": self.file1.hash,
            "tag": self.tag1.id,
        }], content_type="application/json")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(models.FileTag.objects.count(), 2)

    def test_delete_does_not_exist(self):
        models.FileTag.objects.create(file_id=self.file1.hash, tag_id=self.tag1.id)
        models.FileTag.objects.create(file_id=self.file1.hash, tag_id=self.tag2.id)
        models.FileTag.objects.create(file_id=self.file2.hash, tag_id=self.tag1.id)
        self.assertEqual(models.FileTag.objects.count(), 3)
        response = self.client.delete(self.url, [{
            "file": self.file1.hash,
            "tag": self.tag1.id,
        }, {
            "file": "hash8",
            "tag": self.tag1.id,
        }], content_type="application/json")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(models.FileTag.objects.count(), 2)
