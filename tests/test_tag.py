from django.test import TestCase, Client
from django.urls import reverse

from vgloss import actions, models

class TestTagUpdateAction(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("api-action")

    def action_request(self, *actions, assert_status_code=200):
        response = self.client.post(self.url, [
            action.serialize()
            for action in actions
        ], content_type="application/json")
        if assert_status_code is not None:
            self.assertEqual(response.status_code, assert_status_code, response.data)
        for action_status in response.data:
            self.assertEqual(action_status.get("status"), "completed")
        return response

    def test_create(self):

        # Create first tag
        response = self.action_request(
            actions.TagUpdate(tags=[
                {"name": "tag1"},
            ])
        )
        self.assertSetEqual(
            set(models.Tag.objects.values_list("name", flat=True)),
            {"tag1"}
        )
        tag1 = models.Tag.objects.get(name="tag1")
        self.assertListEqual(
            response.data,
            [
                {
                    "status": "completed",
                    "extraActions": [
                        actions.TagUpdate(tags=[
                            {"id": tag1.id, "name": "tag1", "parent": None},
                        ]).serialize()
                    ]
                }
            ]
        )

        # Create another tag
        response = self.action_request(
            actions.TagUpdate(tags=[
                {"id": tag1.id, "name": "tag1"},
                {"name": "tag2", "parent": tag1.id},
            ])
        )
        self.assertSetEqual(
            set(models.Tag.objects.values_list("name", flat=True)),
            {"tag1", "tag2"}
        )
        tag2 = models.Tag.objects.get(name="tag2")
        self.assertListEqual(
            response.data,
            [
                {
                    "status": "completed",
                    "extraActions": [
                        actions.TagUpdate(tags=[
                            {"id": tag1.id, "name": "tag1", "parent": None},
                            {"id": tag2.id, "name": "tag2", "parent": tag1.id},
                        ]).serialize()
                    ]
                }
            ]
        )

    def test_create_temp_id(self):
        """
        Frontend can pass temporary string IDs for tags before they are
        saved to the database.
        """
        # Create two tags with a relationship
        # (not possible temporary IDs)
        response = self.action_request(
            actions.TagUpdate(tags=[
                {"id": "temp1", "name": "tag1", "parent": None},
                {"id": "temp2", "name": "tag2", "parent": "temp1"},
            ])
        )
        tag1 = models.Tag.objects.get(name="tag1")
        tag2 = models.Tag.objects.get(name="tag2")

        self.assertListEqual(
            response.data,
            [
                {
                    "status": "completed",
                    "extraActions": [
                        actions.TagUpdate(tags=[
                            {"id": tag1.id, "name": "tag1", "parent": None},
                            {"id": tag2.id, "name": "tag2", "parent": tag1.id},
                        ]).serialize()
                    ]
                }
            ]
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

        response = self.action_request(
            actions.TagUpdate(tags=[
                {"id": tag1.id, "name": "New Name!"},
            ])
        )

        self.assertListEqual(
            response.data,
            [
                {
                    "status": "completed",
                    "extraActions": [
                        actions.TagUpdate(tags=[
                            {"id": models.Tag.objects.get().id, "name": "New Name!", "parent": None},
                        ]).serialize()
                    ]
                }
            ]
        )

        tag1.refresh_from_db()
        self.assertEqual(tag1.name, "New Name!")

    def test_update_bad_id(self):
        """Test updating a non-existant tag ID."""
        # IDs are assigned by backend, not frontend. If a tag ID doesn't exist
        # a 404 should be raised.
        response = self.action_request(
            actions.TagUpdate(tags=[
                {"id": 8, "name": "New Name!"},
            ])
        )
        self.assertListEqual(
            response.data,
            [
                {
                    "status": "completed",
                    "extraActions": [
                        actions.TagUpdate(tags=[]).serialize()
                    ]
                }
            ]
        )
        self.assertEqual(models.Tag.objects.count(), 0)

    def test_delete(self):
        _ = models.Tag.objects.create(name="tag1")
        tag2 = models.Tag.objects.create(name="tag2")
        _ = models.Tag.objects.create(name="tag3")
        tag4 = models.Tag.objects.create(name="tag4")

        response = self.action_request(
            actions.TagUpdate(tags=[
                {"id": tag2.id, "name": "tag2_updated"},
                {"id": tag4.id, "name": "tag4_updated"},
            ])
        )
        self.assertListEqual(
            response.data,
            [
                {
                    "status": "completed",
                    "extraActions": [
                        actions.TagUpdate(tags=[
                            {"id": tag2.id, "name": "tag2_updated", "parent": None},
                            {"id": tag4.id, "name": "tag4_updated", "parent": None},
                        ]).serialize()
                    ]
                }
            ]
        )
        self.assertSetEqual(
            set(models.Tag.objects.values_list("id", flat=True)),
            {tag2.id, tag4.id}
        )
        self.assertSetEqual(
            set(models.Tag.objects.values_list("name", flat=True)),
            {"tag2_updated", "tag4_updated"}
        )

    def test_delete_cascade(self):
        """Deleting a tag cascades to its child tags."""
        tag1 = models.Tag.objects.create(name="tag1")
        tag2 = models.Tag.objects.create(name="tag2", parent=tag1)
        tag3 = models.Tag.objects.create(name="tag3", parent=tag2)
        tag4 = models.Tag.objects.create(name="tag4")

        # Keep everything but 1, which cascade deletes 2 and 3.
        response = self.action_request(
            actions.TagUpdate(tags=[
                {"id": tag2.id, "name": "tag2"},
                {"id": tag3.id, "name": "tag3"},
                {"id": tag4.id, "name": "tag4"},
            ])
        )
        self.assertListEqual(
            response.data,
            [
                {
                    "status": "completed",
                    "extraActions": [
                        actions.TagUpdate(tags=[
                            {"id": tag4.id, "name": "tag4", "parent": None},
                        ]).serialize()
                    ]
                }
            ]
        )
        self.assertSetEqual(
            set(models.Tag.objects.values_list("id", flat=True)),
            {tag4.id}
        )
