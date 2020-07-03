from django.test import TestCase, Client
from django.urls import reverse

from vgloss import models

class TestTag(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("api-tags")

    def test_list(self):
        models.Tag.objects.create(name="tag1")
        models.Tag.objects.create(name="tag2")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.data,
            [
                {"id": 1, "name": "tag1"},
                {"id": 2, "name": "tag2"},
            ]
        )

    def test_create(self):

        # Create first tag
        response = self.client.post(self.url, [{
            "name": "tag1",
        }], content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(
            set(models.Tag.objects.values_list("name", flat=True)),
            {"tag1"}
        )
        self.assertListEqual(
            response.data,
            [{"id": models.Tag.objects.get().id, "name": "tag1"}]
        )

        # Create another tag
        response = self.client.post(self.url, response.data + [{
            "name": "tag2",
        }], content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(
            set(models.Tag.objects.values_list("name", flat=True)),
            {"tag1", "tag2"}
        )
        self.assertListEqual(
            response.data,
            [
                {"id": models.Tag.objects.get(name="tag1").id, "name": "tag1"},
                {"id": models.Tag.objects.get(name="tag2").id, "name": "tag2"},
            ]
        )

    def test_update(self):
        tag1 = models.Tag.objects.create(name="tag1")

        response = self.client.post(self.url, [{
            "id": tag1.id,
            "name": "New Name!",
        }], content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.data,
            [
                {"id": models.Tag.objects.get().id, "name": "New Name!"},
            ]
        )

        tag1.refresh_from_db()
        self.assertEqual(tag1.name, "New Name!")

    def test_update_bad_id(self):
        """Test updating a non-existant tag ID."""
        # IDs are assigned by backend, not frontend. If a tag ID doesn't exist
        # a 404 should be raised.
        response = self.client.post(self.url, [{
            "id": 8,
            "name": "New Name!",
        }], content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(models.Tag.objects.count(), 0)

    def test_delete(self):
        tag1 = models.Tag.objects.create(name="tag1")
        models.Tag.objects.create(name="tag2")

        response = self.client.post(self.url, [{
            "id": tag1.id,
            "name": "tag1",
        }], content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(
            set(models.Tag.objects.values_list("name", flat=True)),
            {"tag1"}
        )
        self.assertListEqual(
            response.data,
            [
                {"id": models.Tag.objects.get().id, "name": "tag1"},
            ]
        )
