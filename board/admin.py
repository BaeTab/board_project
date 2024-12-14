from django.contrib import admin
from .models import Post, Comment, Like

# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at']
    search_fields = ['title', 'content']
    list_filter = ['created_at']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'created_at']
    search_fields = ['content']
    list_filter = ['created_at']

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']
    list_filter = ['created_at']
