from django.contrib import admin
from vgloss import models

class AdminSite(admin.AdminSite):
    enable_nav_sidebar = False
    index_title="HELLO!"

admin.site.register(models.File)
admin.site.register(models.FilePath)
admin.site.register(models.Tag)
admin.site.register(models.FileTag)
