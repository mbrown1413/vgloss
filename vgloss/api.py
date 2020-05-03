from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response

import magic

from . import models

class GalleryQuery(APIView):
    """Query for a list of images."""

    def get(self, request, *args, **kwargs):
        return Response([
            dict(
                name=file.hash,
                hash=file.hash,
            )
            for file in models.File.objects.all()
        ])

class Image(APIView):
    """Retrieve raw image from image hash."""

    def get(self, request, hash):
        file = get_object_or_404(models.File, hash=hash)
        mimetype = magic.from_file(file.abspath, mime=True)
        with open(file.abspath, "rb") as f:
            return HttpResponse(f.read(), mimetype)

class ImageThumbnail(APIView):
    """Retrieve thumbnail for an image hash."""

    def get(self, request, hash):
        file = get_object_or_404(models.File, hash=hash)
        path = file.get_thumbnail_path()
        if not path:
            raise Http404()
        with open(path, "rb") as f:
            return HttpResponse(f.read(), "image/jpeg")
