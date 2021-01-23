import os
import posixpath
import mimetypes
from functools import lru_cache

from django.conf import settings
from django.views.generic import View
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render

from . import models, serializers


DIST_DIR = os.path.join(settings.VGLOSS_CODE_DIR, "dist")


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

@lru_cache()
def read_dist_file(path):
    path = posixpath.normpath(path).lstrip("/")
    abspath = os.path.abspath(os.path.join(DIST_DIR, path))

    if os.path.commonpath([abspath, DIST_DIR]) != DIST_DIR:
        # abspath must be within DIST_DIR
        return None, None, None
    if not os.path.exists(abspath) or os.path.isdir(abspath):
        return None, None, None

    content_type, encoding = mimetypes.guess_type(abspath)
    content_type = content_type or 'application/octet-stream'
    is_bin = content_type.startswith("image/")
    content = open(abspath, "rb" if is_bin else "r").read()
    return content, content_type, encoding

class DistFile(View):
    fall_back_to_index = False

    def get(self, request, *args, **kwargs):
        content, content_type, encoding = read_dist_file(request.path)

        # Fallback to serving index.html
        if self.fall_back_to_index and not content:
            return render(
                request,
                "vgloss/vue-single-page.html",
                context={
                    "metadata": initial_pageload_data(),
                },
            )

        #TODO: This view should do some things that django.views.static.serve
        #      does. Namely:
        #      * Respect HTTP_IF_MODIFIED_SINCE header
        #      * Send Last-Modified header

        response = HttpResponse(
            content=content,
            content_type=content_type,
        )
        if encoding:
            response["Content-Encoding"] = encoding
        return response

class VueSinglePage(DistFile):
    fall_back_to_index = True

class File(View):
    """Retrieve raw image from image hash."""

    def get(self, request, hash):
        file = get_object_or_404(models.File, hash=hash)
        with open(file.abspath, "rb") as f:
            return HttpResponse(f.read(), f.mimetype)

class FileThumbnail(View):
    """Retrieve thumbnail for an image hash."""

    def get(self, request, hash):
        file = get_object_or_404(models.File, hash=hash)
        path = file.get_thumbnail_path()
        if not path:
            raise Http404()
        with open(path, "rb") as f:
            return HttpResponse(f.read(), "image/jpeg")
