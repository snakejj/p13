from django.contrib import admin

from .models import Comment


class CommentAdmin(admin.ModelAdmin):

    list_display = ('added_on', 'status', 'video', 'pseudo', 'email', "message")
    list_filter = ('status',)


admin.site.register(Comment, CommentAdmin)
