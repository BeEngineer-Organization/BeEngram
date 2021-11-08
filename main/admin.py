from django.contrib import admin

from .models import Comment, Post, User

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
