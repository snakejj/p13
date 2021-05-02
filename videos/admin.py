from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html

from .models import Video, AbuseVideo, RateVideo


class VideoAdmin(admin.ModelAdmin):

    list_display = ('pk', 'status', 'link', 'added_on')
    list_filter = ('status',)


admin.site.register(Video, VideoAdmin)


class AbuseVideoAdmin(admin.ModelAdmin):

    list_display = ('pk', 'added_on', 'video', "reason", 'message',)
    list_filter = ('reason',)


admin.site.register(AbuseVideo, AbuseVideoAdmin)


class RateVideoAdmin(admin.ModelAdmin):

    list_display = ('pk', 'video', 'interest_rating', 'quality_rating',)
    list_filter = ('interest_rating', 'quality_rating')


admin.site.register(RateVideo, RateVideoAdmin)
