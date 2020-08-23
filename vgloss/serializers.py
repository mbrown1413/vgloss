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
            tag_ids = [t.get("id") for t in self.validated_data]
            tags_qs = models.Tag.objects.filter(id__in=tag_ids)
            tag_mapping = {tag.id: tag for tag in tags_qs}

            # Perform creation / update
            for tag_data in self.validated_data:
                tag_id = tag_data.get("id")
                if tag_id is None:
                    tag = None
                else:
                    tag = tag_mapping.get(tag_id)
                    if tag is None:
                        raise NotFound(f'ID {tag_id} not found', 404)
                if tag is None:
                    self.child.create(tag_data)
                else:
                    self.child.update(tag, tag_data)

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
