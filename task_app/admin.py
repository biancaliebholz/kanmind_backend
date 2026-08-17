from django.contrib import admin

from .models import Comment, Task


admin.site.register(Task)
admin.site.register(Comment)