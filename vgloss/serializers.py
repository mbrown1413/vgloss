from copy import deepcopy

from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from vgloss import models, actions


class ActionSerializer(serializers.Serializer):

    def to_internal_value(self, data):
        class_name = data.get("type")
        if not class_name:
            raise serializers.ValidationError("Action type is required")
        try:
            cls = actions.ACTION_CLASSES[class_name]
        except KeyError as e:
            raise serializers.ValidationError("Invalid action type given") from e
        return cls(**data["data"])

class FileSerializer(serializers.ModelSerializer):
    tags = serializers.ReadOnlyField(source="tag_ids")

    class Meta:
        model = models.File
        fields = [
            "hash", "name", "is_image", "timestamp", "tags",
            #"size",
        ]

class FileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.File
        fields = [
            "mimetype", "metadata", "paths",
        ]

class TagListSerializer(serializers.ListSerializer):

    def to_internal_value(self, data):
        data = deepcopy(data)

        # If the frontend sends a string ID, it is a temporary ID. Remove it
        # here so it will validate. Later, in save(), we'll look at
        # initial_data to resolve the temporary IDs in the parent links to real
        # ones.
        for tag in data:
            if isinstance(tag.get("id"), str):
                del tag["id"]
            if isinstance(tag.get("parent"), str):
                tag["parent"] = None

        return super().to_internal_value(data)

    def save(self, delete_unseen=False, ignore_not_found=False):
        with atomic():
            tag_ids = [t.get("id") for t in self.validated_data]
            tags_qs = models.Tag.objects.filter(id__in=tag_ids)
            tag_map = {tag.id: tag for tag in tags_qs}

            # Perform creation / update
            saved_tags = []
            for tag_data in self.validated_data:
                tag_id = tag_data.get("id")
                if tag_id is None:
                    tag = None
                else:
                    tag = tag_map.get(tag_id)
                    if tag is None:
                        if not ignore_not_found:
                            raise NotFound(f'ID {tag_id} not found', 404)
                        else:
                            continue
                if tag is None:
                    tag = self.child.create(tag_data)
                else:
                    self.child.update(tag, tag_data)
                saved_tags.append(tag)

            # Handle temporary IDs
            # Strings in id or parent fields are temporary IDs. They are
            # present in initial_data but removed in validation. We take a
            # 2-pass approach to saving tags that used temporary IDs to
            # reference their parent.
            #
            # 1) Get a mapping of temp IDs to the real ID that was saved in the
            # database.
            temp_id_map = {}
            for tag, initial_tag_data in zip(saved_tags, self.initial_data):
                temp_tag_id = initial_tag_data.get("id")
                if isinstance(temp_tag_id, str):
                    temp_id_map[temp_tag_id] = tag.id
            # 2) Find tags with temp IDs in their parent field and re-save them
            # with the real ID.
            for tag, initial_tag_data in zip(saved_tags, self.initial_data):
                temp_parent_id = initial_tag_data.get("parent")
                if isinstance(temp_parent_id, str):
                    tag.parent_id = temp_id_map[temp_parent_id]
                    tag.save()

            # Delete unseen tags
            # Do this last, since we want to be sure the delete cascades to
            # everything needed.
            if delete_unseen:
                saved_tag_ids = [t.id for t in saved_tags]
                unseen_tags = models.Tag.objects.exclude(id__in=saved_tag_ids)
                unseen_tags.delete()

    def delete(self):
        with atomic():
            tag_ids = [t.get("id") for t in self.initial_data]
            tags_qs = models.Tag.objects.filter(id__in=tag_ids)
            tags_qs.delete()

class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = models.Tag
        fields = ["id", "name", "parent"]
        list_serializer_class = TagListSerializer

class FileTagListSerializer(serializers.ListSerializer):

    def save(self):
        with atomic():
            for filetag in self.validated_data:
                models.FileTag.objects.get_or_create(
                    file_id=filetag["file_hash"],
                    tag_id=filetag["tag_id"],
                )

    def delete(self):
        with atomic():
            for filetag in self.validated_data:
                models.FileTag.objects.filter(
                    file_id=filetag["file_hash"],
                    tag_id=filetag["tag_id"],
                ).delete()

class FileTagSerializer(serializers.ModelSerializer):
    file = serializers.CharField(source="file_hash")
    tag = serializers.IntegerField(source="tag_id")

    class Meta:
        model = models.FileTag
        fields = ["file", "tag"]
        list_serializer_class = FileTagListSerializer
