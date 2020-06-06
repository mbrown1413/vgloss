import os

from django.conf import settings

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from . import models, serializers


def get_folder_tree(path):
    tree = {}
    for entry in os.scandir(path):
        if entry.name == ".vgloss":
            continue
        elif entry.is_dir() and not entry.is_symlink():
            tree[entry.name] = get_folder_tree(entry.path)
    return tree

class GalleryApi(APIView):
    """Retrieve global information needed to show the gallery."""

    def get(self, *args, **kwargs):
        return Response(dict(
            folderTree=get_folder_tree(settings.BASE_DIR),
        ))


class FileListApi(APIView):

    def get(self, *args, **kwargs):
        qs = models.File.objects.all()

        # Filter by folder
        folder = self.request.GET.get("folder")
        if folder is not None:
            folder = folder.strip("/")
            paths = models.FilePath.objects.filter(folder=folder)
            qs = qs.filter(paths__in=paths).distinct()

        file_serializer = serializers.FileSerializer(qs, many=True)
        return Response(file_serializer.data)

class FileDetailApi(generics.RetrieveAPIView):
    queryset = models.File.objects.all()
    serializer_class = serializers.FileDetailSerializer
    lookup_field = "hash"
