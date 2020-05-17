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
