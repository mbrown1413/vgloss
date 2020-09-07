from django.test import TestCase, Client
from django.urls import reverse

from vgloss import models

class TestTag(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("api-tags")

    def test_list(self):
        tag1 = models.Tag.objects.create(name="tag1")
        models.Tag.objects.create(name="tag2", parent=tag1)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.data,
            [
                {"id": 1, "name": "tag1", "parent": None},
                {"id": 2, "name": "tag2", "parent": tag1.id},
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
        tag1 = models.Tag.objects.get(name="tag1")
        self.assertListEqual(
            response.data,
            [{"id": models.Tag.objects.get().id, "name": "tag1", "parent": None}]
        )

        # Create another tag
        response = self.client.post(self.url, response.data + [{
            "name": "tag2",
            "parent": tag1.id,
        }], content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(
            set(models.Tag.objects.values_list("name", flat=True)),
            {"tag1", "tag2"}
        )
        tag2 = models.Tag.objects.get(name="tag2")
        self.assertListEqual(
            response.data,
            [
                {"id": tag1.id, "name": "tag1", "parent": None},
                {"id": tag2.id, "name": "tag2", "parent": tag1.id},
            ]
        )

    def test_create_temp_id(self):
        """
        Frontend can pass temporary string IDs for tags before they are
        saved to the database.
        """
        # Create two tags with a relationship
        # (not possible temporary IDs)
        response = self.client.post(self.url, [
            {"id": "temp1", "name": "tag1", "parent": None},
            {"id": "temp2", "name": "tag2", "parent": "temp1"},
        ], content_type="application/json")
        self.assertEqual(response.status_code, 200)
        tag1 = models.Tag.objects.get(name="tag1")
        tag2 = models.Tag.objects.get(name="tag2")
        self.assertSetEqual(
            set(tuple(tag.items()) for tag in response.data),
            {
                tuple({"id": tag1.id, "name": "tag1", "parent": None}.items()),
                tuple({"id": tag2.id, "name": "tag2", "parent": tag1.id}.items()),
            }
        )
        self.assertSetEqual(
            set(tuple(tag.items()) for tag in models.Tag.objects.values()),
            {
                tuple({"id": tag1.id, "name": "tag1", "parent_id": None}.items()),
                tuple({"id": tag2.id, "name": "tag2", "parent_id": tag1.id}.items()),
            }
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
                {"id": models.Tag.objects.get().id, "name": "New Name!", "parent": None},
            ]
        )

        tag1.refresh_from_db()
        self.assertEqual(tag1.name, "New Name!")

    def test_update_multiple(self):
        tag1 = models.Tag.objects.create(name="tag1")
        tag2 = models.Tag.objects.create(name="tag2")

        # Modify 2 at once
        response = self.client.post(self.url, [
            {
            "id": tag1.id,
            "name": "modified1",
            },
            {
            "id": tag2.id,
            "name": "modified2",
            },
        ], content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.data,
            [
                {"id": tag1.id, "name": "modified1", "parent": None},
                {"id": tag2.id, "name": "modified2", "parent": None},
            ]
        )

        tag1.refresh_from_db()
        tag2.refresh_from_db()
        self.assertEqual(tag1.name, "modified1")
        self.assertEqual(tag2.name, "modified2")

        # Modify one but not the other
        response = self.client.post(self.url, [
            {"id": tag2.id, "name": "modified2 again", "parent": tag1.id},
        ], content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.data,
            [
                {"id": tag1.id, "name": "modified1", "parent": None},
                {"id": tag2.id, "name": "modified2 again", "parent": tag1.id},
            ]
        )

        tag1.refresh_from_db()
        tag2.refresh_from_db()
        self.assertEqual(tag1.name, "modified1")
        self.assertEqual(tag2.name, "modified2 again")

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
        tag2 = models.Tag.objects.create(name="tag2")
        tag3 = models.Tag.objects.create(name="tag3")
        tag4 = models.Tag.objects.create(name="tag4")

        response = self.client.delete(self.url, [
            {"id": tag1.id},
            {"id": tag3.id},
        ], content_type="application/json")
        self.assertEqual(response.status_code, 204)
        self.assertSetEqual(
            set(models.Tag.objects.values_list("id", flat=True)),
            {tag2.id, tag4.id}
        )

    def test_delete_cascade(self):
        """Deleting a tag cascades to its child tags."""
        tag1 = models.Tag.objects.create(name="tag1")
        tag2 = models.Tag.objects.create(name="tag2", parent=tag1)
        _ = models.Tag.objects.create(name="tag3", parent=tag2)
        tag4 = models.Tag.objects.create(name="tag4")

        response = self.client.delete(self.url, [
            {"id": tag1.id},
        ], content_type="application/json")
        self.assertEqual(response.status_code, 204)
        self.assertSetEqual(
            set(models.Tag.objects.values_list("id", flat=True)),
            {tag4.id}
        )
