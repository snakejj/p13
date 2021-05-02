from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html

from .models import Video, AbuseVideo, RateVideo


class VideoAdmin(admin.ModelAdmin):

    list_display = ('pk', 'status', 'link', 'added_on', 'average_interest_rating', 'average_quality_rating')
    list_filter = ('status',)


admin.site.register(Video, VideoAdmin)


class VideoReportedFilter(admin.SimpleListFilter):
    title = 'video_id'
    parameter_name = 'video'

    def lookups(self, request, model_admin):
        if 'report_dealt_with__exact' in request.GET:
            id = request.GET['report_dealt_with__exact']
            videos = set([c.video for c in model_admin.model.objects.all().filter(report_dealt_with=id)])
        else:
            videos = set([c.video for c in model_admin.model.objects.all()])
        return [(s.pk, s.pk) for s in videos]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(video__id__exact=self.value())


class AbuseVideoAdmin(admin.ModelAdmin):

    list_display = ('pk', 'report_dealt_with', 'added_on', 'video', "reason", 'message',)
    list_filter = ('report_dealt_with', VideoReportedFilter,)
    actions = ["mark_dealt_with"]

    def mark_dealt_with(self, request, queryset):
        queryset.update(report_dealt_with=True)


admin.site.register(AbuseVideo, AbuseVideoAdmin)


class RateVideoAdmin(admin.ModelAdmin):

    list_display = (
        'pk',
        'video',
        'interest_rating',
        'quality_rating',
    )


admin.site.register(RateVideo, RateVideoAdmin)
