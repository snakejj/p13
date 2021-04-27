from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html

from .models import Video, AbuseVideo


class VideoAdmin(admin.ModelAdmin):

    list_display = ('pk', 'status', 'link', 'added_on')
    list_filter = ('status',)


admin.site.register(Video, VideoAdmin)


class AbuseVideoAdmin(admin.ModelAdmin):

    list_display = ('pk', 'added_on', 'video', "reason", 'message',)
    list_filter = ('reason',)


admin.site.register(AbuseVideo, AbuseVideoAdmin)