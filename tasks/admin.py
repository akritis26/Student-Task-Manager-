from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'due_date', 'priority', 'status', 'user')
    list_filter = ('priority', 'status', 'subject')
    search_fields = ('title', 'subject', 'description')