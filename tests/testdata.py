import os
import shutil

from django.conf import settings

from PIL import Image

def make_path(path):
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
    Image.new("RGB", (100, 100), (0, 0, 0)).save(make_path("black_square1.jpg"))
    Image.new("RGB", (100, 100), (255, 255, 255)).save(make_path("white_square.jpg"))
    shutil.copy(make_path("black_square1.jpg"), make_path("black_square2.jpg"))
    os.mkdir(make_path("dir1"))
    shutil.copy(make_path("black_square1.jpg"), make_path("dir1/black_square3.jpg"))

    with open(make_path("not_image.txt"), "w") as f:
        f.write("I am a lonely text file.")
