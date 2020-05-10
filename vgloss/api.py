import os

from django.conf import settings
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response

from . import models

class GalleryQuery(APIView):
    """Query for a list of images."""

    def get(self, request, *args, **kwargs):
        qs = models.File.objects.all()

        # Filter files based on folder
        folder = request.GET.get("folder")
        if folder is not None:
            folder = folder.strip("/")
            paths = models.FilePath.objects.filter(folder=folder)
            qs = qs.filter(paths__in=paths).distinct()

        response = dict(
            files=[
                dict(
                    name=file.name,
                    hash=file.hash,
                )
                for file in qs
            ]
        )
        if folder is not None:
            folder_abspath = os.path.normpath(os.path.join(settings.BASE_DIR, folder))
            if not os.path.commonpath([folder_abspath, settings.BASE_DIR]) == settings.BASE_DIR:
                raise Http404()
            try:
                files = os.listdir(folder_abspath)
            except FileNotFoundError:
                raise Http404()
            response["folders"] = [
                f
                for f in files
                if os.path.isdir(os.path.join(folder_abspath, f))
                if f != ".vgloss"
            ]

        return Response(response)
