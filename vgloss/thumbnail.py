import os
import subprocess

from . import models

THUMBNAIL_VERSION = 0

def generate_all_thumbnails():
    updated_files = []
    for file in models.File.objects.iterator():
        if not file.is_image:
            continue

        thumbnail_path = file.get_thumbnail_path(_absent_ok=True)
        if not os.path.exists(thumbnail_path) or file.thumbnail_version is None or file.thumbnail_version < THUMBNAIL_VERSION:
            generate_thumbnail(file, thumbnail_path)
            file.thumbnail_version = THUMBNAIL_VERSION
            updated_files.append(file)
    models.File.objects.bulk_update(updated_files, ["thumbnail_version"])

def generate_thumbnail(file, out_path):
    file_path = file.paths.first()
    if not file_path:
        # No actual file to back this, so we can't read the thumbnail!
        return

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    subprocess.check_call([
        "vipsthumbnail", file_path.abspath,
        "-o", out_path+"[Q=50,optimize_coding,interlace,strip]",
        "--size", "250",
        "--rotate",
        "--eprofile", "/usr/share/color/icc/sRGB.icc",
    ])
