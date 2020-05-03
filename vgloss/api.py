from rest_framework.views import APIView
from rest_framework.response import Response

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
