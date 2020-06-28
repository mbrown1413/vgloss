from django.db.transaction import atomic
from rest_framework import serializers

from vgloss import models


class FileSerializer(serializers.ModelSerializer):
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
                tag = tag_mapping.get(tag_id, None)
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
