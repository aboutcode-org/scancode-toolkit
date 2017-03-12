from django.contrib import admin

# Register your models here.

from handler.models import Files
from django.contrib import admin

class FilesAdmin(admin.ModelAdmin):
    list_display = ('created', 'docfile')

admin.site.register(Files, FilesAdmin)

