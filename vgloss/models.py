import os

from django.db import models
from django.conf import settings

class File(models.Model):
    hash = models.TextField(primary_key=True)

    # We track the versions so if code changes we can trigger an update.
    scan_version = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    thumbnail_version = models.PositiveIntegerField(blank=True, null=True)

    # Scanned Data
    SCAN_FIELDS = ("timestamp", "exif_json")
    timestamp = models.DateTimeField(blank=True, null=True, db_index=True)
    exif_json = models.TextField(blank=True, null=True)

    def get_thumbnail_path(self, _absent_ok=False):
        path = os.path.join(settings.THUMBNAIL_DIR, self.hash+".jpg")
        if _absent_ok or os.path.exists(path):
            return path
        else:
            return None

class FilePath(models.Model):
    path = models.TextField(primary_key=True)
    file = models.ForeignKey("File", db_column="file_hash", related_name="paths", on_delete=models.PROTECT)
    st_mtime_ns = models.BigIntegerField()

    @property
    def abspath(self):
        path = os.path.abspath(os.path.join(settings.BASE_DIR, self.path))
        assert path.startswith(settings.BASE_DIR)
        return path
