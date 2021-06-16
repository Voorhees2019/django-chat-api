from django.contrib import admin
from .models import Thread, Message


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "created_at", "updated_at")
    list_display_links = ("id", "__str__")
    raw_id_fields = ("participants",)
    list_per_page = 25


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "thread", "sender", "created_at", "updated_at")
    list_display_links = ("id", "thread")
    list_filter = ("sender", "thread")
    search_fields = ("sender__email", "sender__username")
    list_per_page = 25
