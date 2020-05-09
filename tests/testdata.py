import os
import shutil

from django.conf import settings

from PIL import Image

def _path(path):
    return os.path.join(settings.BASE_DIR, path)

def clean():
    for entry in os.scandir(settings.BASE_DIR):
        path = os.path.join(settings.BASE_DIR, entry.name)
        if entry.is_dir():
            shutil.rmtree(path)
        else:
            os.remove(path)

def basic_data():
    clean()
    Image.new("RGB", (100, 100), (0, 0, 0)).save(_path("black_square.jpg"))
    Image.new("RGB", (100, 100), (255, 255, 255)).save(_path("white_square.jpg"))
    shutil.copy(_path("black_square.jpg"), _path("black_square2.jpg"))
