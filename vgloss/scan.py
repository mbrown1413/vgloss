import os
import hashlib

from django.conf import settings

from . import models

SCAN_VERSION = 0

def _list_paths(root):
    for cwd, dirs, paths in os.walk(root):
        if cwd.startswith(settings.DATA_DIR):
            continue
        for path in paths:
            abspath = os.path.join(cwd, path)
            yield os.path.relpath(abspath, root), abspath

def _get_file_hash(abspath):
    assert os.path.isabs(abspath)
    h = hashlib.md5()
    with open(abspath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def _get_stale_paths():
    # Collect all FilePaths from database.
    # Query for all FilePaths up front and index them in a dictionary key'd by
    # path. This allows us to know what's already in the database by making a
    # single database call, which will be much faster than making a database
    # call for every path we see.
    file_paths = {}
    for file_path in models.FilePath.objects.all().iterator():
        file_paths[file_path.path] = file_path

    # Inspect each file in the directory
    for path, abspath in _list_paths(settings.BASE_DIR):
        try:
            stat = os.stat(abspath)
        except FileNotFoundError:
            # Race condition if file gets deleted. Act like we never saw it in
            # the first place.
            continue

        if path in file_paths:
            # File is already in database. Has it changed?
            file_path = file_paths.pop(path)
            if stat.st_mtime_ns > file_path.st_mtime_ns:
                file_path.st_mtime_ns = stat.st_mtime_ns
                file_path.hash = _get_file_hash(abspath)
                yield file_path, "updated"
        else:
            # File wasn't in database. Yield unsaved object
            yield models.FilePath(
                path=path,
                file_id=_get_file_hash(abspath),
                st_mtime_ns=stat.st_mtime_ns,
            ), "created"
            continue

    # Paths in database we didn't see were deleted
    for file_path in file_paths.values():
        yield file_path, "deleted"

def scan_all():

    # Gather FilePaths we need to create or update
    to_create = []
    to_update = []
    to_delete = []
    referenced_hashes = set()
    for file_path, action in _get_stale_paths():
        if action == "created":
            referenced_hashes.add(file_path.file_id)
            to_create.append(file_path)
        elif action == "updated":
            referenced_hashes.add(file_path.file_id)
            to_update.append(file_path)
        elif action == "deleted":
            to_delete.append(file_path.path)

    # Ensure all referenced File objects exist
    existing_hashes = models.File.objects.filter(
        hash__in=referenced_hashes
    ).values_list("hash", flat=True)
    referenced_hashes.difference_update(existing_hashes)
    models.File.objects.bulk_create(
        [models.File(hash=hash) for hash in referenced_hashes]
    )
    del existing_hashes
    del referenced_hashes

    # FilePath Create, Update, Delete
    if to_create:
        models.FilePath.objects.bulk_create(to_create)
    if to_update:
        models.FilePath.objects.bulk_update(to_update, ["file", "st_mtime_ns"])
    if to_delete:
        models.FilePath.objects.filter(path__in=to_delete).delete()
    del to_create
    del to_update
    del to_delete

    # Remove Files with no FilePath
    #TODO: At some point we could keep these around in case the images get put
    #      back. This would preserve tags, comments, etc. pointing to them. We
    #      might have to hide them in the UI though, or maybe put a warning in
    #      front of them?
    models.File.objects.filter(paths__isnull=True).delete()

    # Scan outdated files
    outdated_files =list(
        models.File.objects.exclude(scan_version__gte=SCAN_VERSION)
    )
    for file_obj in outdated_files:
        scan_file(file_obj)
    models.File.objects.bulk_update(outdated_files, models.File.SCAN_FIELDS)

def scan_file(file_obj):
    # Extract exif
    #TODO

    # Extract time
    #TODO

    file_obj.scan_version = SCAN_VERSION
    file_obj.save()
