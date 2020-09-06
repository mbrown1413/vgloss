from django.contrib import admin

from vgloss import models

admin.site.register(models.File)
admin.site.register(models.FilePath)
admin.site.register(models.Tag)
admin.site.register(models.FileTag)
