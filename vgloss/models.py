import os
import json

from django.db import models
from django.conf import settings
from django.urls import reverse

class File(models.Model):
    hash = models.TextField(primary_key=True) # SHA-512
    name = models.TextField()
    mimetype = models.TextField()
    #size = models.PositiveIntegerField()

    # Track code versions so if code changes we can trigger an update.
    scan_version = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    thumbnail_version = models.PositiveIntegerField(blank=True, null=True)

    # Scanned Data
    SCAN_FIELDS = ("timestamp", "metadata_json")
    metadata_json = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True, db_index=True)

    @property
    def is_image(self):
        return self.mimetype.startswith("image/")

    @property
    def metadata(self):
        return json.loads(self.metadata_json)

    @metadata.setter
    def metadata(self, data):
        self.metadata_json = json.dumps(data)

    @property
    def thumbnail_url(self):
        return reverse("file-thumb", kwargs={"hash": self.hash})

    def get_thumbnail_path(self, _absent_ok=False):
        path = os.path.join(settings.THUMBNAIL_DIR, self.hash+".jpg")
        if _absent_ok or os.path.exists(path):
            return path
        else:
            return None

    @property
    def paths(self):
        return self.paths.objects.values_list("path")

class FilePath(models.Model):
    path = models.TextField(primary_key=True)
    folder = models.TextField(db_index=True)  # Redundanct with path, used for querying
    filename = models.TextField(db_index=True)  # Redundanct with path, used for querying
    file = models.ForeignKey("File", db_column="file_hash", related_name="paths", on_delete=models.PROTECT)
    st_mtime_ns = models.BigIntegerField()

    @property
    def abspath(self):
        path = os.path.abspath(os.path.join(settings.BASE_DIR, self.path))
        assert path.startswith(settings.BASE_DIR)
        return path
