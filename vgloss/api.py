import os

from django.conf import settings

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

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


class TagsApi(GenericAPIView):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.get(request, *args, **kwargs)

class FileTagsApi(GenericAPIView):
    queryset = models.FileTag.objects.all()
    serializer_class = serializers.FileTagSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
