import os
from typing import List

from django.conf import settings
from django.db.transaction import atomic

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
import rest_framework.serializers

from . import models, serializers


def get_folders(path):
    for entry in os.scandir(path):
        if entry.name == ".vgloss":
            continue
        elif entry.is_dir() and not entry.is_symlink():
            yield entry.name
            for subfolder in get_folders(entry.path):
                yield entry.name + "/" + subfolder

def initial_pageload_data():
    """Return data needed on initial pageload."""
    tag_serializer = serializers.TagSerializer(
        models.Tag.objects.all(),
        many=True,
    )
    return dict(
        folders=list(get_folders(settings.BASE_DIR)),
        tags=tag_serializer.data,
    )

class Action(GenericAPIView):
    """Perform one or more actions."""
    serializer_class = serializers.ActionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        actions = serializer.validated_data

        # Do actions
        ret: List[dict] = []
        with atomic():
            for action in actions:
                extra_actions = action.do() or []
                ret.append({
                    "extraActions": list(map(
                        lambda action: action.serialize(),
                        extra_actions
                    )),
                    "status": "completed",
                })

        return Response(ret)


class GalleryApi(APIView):
    """Retrieve global information needed to show the gallery."""
    #TODO: This may be replaced in the future but for now it's unused. This
    #      data is passed in Django templates, and currently nothing updates
    #      this metadata outside of the initial request.

    def get(self, request, *args, **kwargs):
        return Response(initial_pageload_data())


class FileListApi(APIView):

    def get(self, request, *args, **kwargs):
        qs = models.File.objects.all()

        # Filter by folder
        folder = self.request.GET.get("folder")
        if folder is not None:
            folder = folder.strip("/")
            paths = models.FilePath.objects.filter(folder=folder)
            qs = qs.filter(paths__in=paths).distinct()

        # Filter by tag
        tag_str = request.GET.get("tag", "")
        try:
            tag_include = [
                int(t)
                for t in tag_str.split(",")
                if t
            ]
        except ValueError as e:
            raise rest_framework.serializers.ValidationError(
                {"tags": "Tag IDs should be integers"}
            ) from e
        if tag_include:
            qs = qs.filter(tags__in=tag_include)

        file_serializer = serializers.FileSerializer(qs, many=True)
        return Response(file_serializer.data)

class FileDetailApi(generics.RetrieveAPIView):
    queryset = models.File.objects.all()
    serializer_class = serializers.FileDetailSerializer
    lookup_field = "hash"


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
