from django.contrib import admin
from .models import PasswordResetOTP, Post, Comment, Category, Notification, Profile

# admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Notification)
admin.site.register(Profile)
admin.site.register(PasswordResetOTP)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'views', 'total_likes', 'created_at']
    list_filter = ['created_at', 'category']
    search_fields = ['title', 'content']