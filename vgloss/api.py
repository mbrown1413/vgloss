import os

from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response

import magic

class GalleryQuery(APIView):
    """Query for a list of images."""

    def get(self, request, *args, **kwargs):
        names = []
        for filename in os.listdir(settings.BASE_DIR):
            path = os.path.join(settings.BASE_DIR, filename)
            if os.path.isfile(path):
                names.append(filename)

        return Response([
            dict(
                name=name,
                hash=name,
            )
            for name in names
        ])

class ImageThumbnail(APIView):
    """Retrieve thumbnail for an image hash."""

    def get(self, request, filename):
        path = os.path.join(settings.BASE_DIR, filename)
        mimetype = magic.from_file(path, mime=True)
        #TODO: This is obviously not a thumbnail, it's just the whole image.
        with open(path, "rb") as f:
            return HttpResponse(f.read(), mimetype)
