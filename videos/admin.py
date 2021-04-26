from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html

from .models import Video


class VideoAdmin(admin.ModelAdmin):

    list_display = ('pk', 'status', 'link', 'added_on')
    list_filter = ('status',)


admin.site.register(Video, VideoAdmin)
