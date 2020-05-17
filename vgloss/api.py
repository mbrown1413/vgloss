import os

from django.conf import settings
from django.http import Http404

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from . import models, serializers


class FileListAPI(APIView):

    def get(self, *args, **kwargs):
        qs = self.filter_files(models.File.objects.all())
        file_serializer = serializers.FileSerializer(qs, many=True)

        folder = self.request.GET.get("folder")
        if folder:
            folders = self.get_folder_list(folder)
        else:
            folders = []

        return Response(dict(
            files=file_serializer.data,
            folders=folders,
        ))

    def filter_files(self, qs):
        # Filter based on folder
        folder = self.request.GET.get("folder")
        if folder is not None:
            folder = folder.strip("/")
            paths = models.FilePath.objects.filter(folder=folder)
            qs = qs.filter(paths__in=paths).distinct()

        return qs

    def get_folder_list(self, folder):
        folder = folder.strip("/")
        folder_abspath = os.path.normpath(os.path.join(settings.BASE_DIR, folder))
        if not os.path.commonpath([folder_abspath, settings.BASE_DIR]) == settings.BASE_DIR:
            raise Http404()
        try:
            files = os.listdir(folder_abspath)
        except FileNotFoundError:
            raise Http404()
        return [
            f
            for f in files
            if os.path.isdir(os.path.join(folder_abspath, f))
            if f != ".vgloss"
        ]

class FileDetailAPI(generics.RetrieveAPIView):
    queryset = models.File.objects.all()
    serializer_class = serializers.FileDetailSerializer
    lookup_field = "hash"
