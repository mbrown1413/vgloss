from rest_framework import serializers

from vgloss import models


class FileSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ReadOnlyField(source="thumbnail_url")

    class Meta:
        model = models.File
        fields = [
            "hash", "name", "is_image", "timestamp", "thumbnail"
            #"size"
        ]

class FileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.File
        fields = [
            "mimetype", "metadata", "paths"
        ]
