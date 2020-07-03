from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from vgloss import models


class FileSerializer(serializers.ModelSerializer):
    tags = serializers.ReadOnlyField(source="tag_ids")

    class Meta:
        model = models.File
        fields = [
            "hash", "name", "is_image", "timestamp"
            #"size"
        ]

class FileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.File
        fields = [
            "mimetype", "metadata", "paths",
        ]

class TagListSerializer(serializers.ListSerializer):

    def save(self):
        with atomic():
            tag_mapping = {tag.id: tag for tag in models.Tag.objects.all()}

            # Perform creation / update
            saved_tags = []
            for tag_data in self.validated_data:
                tag_id = tag_data.get("id", None)
                if tag_id is None:
                    tag = None
                else:
                    tag = tag_mapping.get(tag_id, None)
                    if tag is None:
                        raise NotFound(f'ID {tag_id} not found', 404)
                if tag is None:
                    saved_tags.append(self.child.create(tag_data))
                else:
                    saved_tags.append(self.child.update(tag, tag_data))

            # Perform deletions
            saved_ids = [tag.id for tag in saved_tags]
            models.Tag.objects.exclude(id__in=saved_ids).delete()

        return saved_tags

class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = models.Tag
        fields = ["id", "name"]
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
