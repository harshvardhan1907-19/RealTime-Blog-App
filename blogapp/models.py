from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()

    parent = models.ForeignKey(
        'self', # This comment can point to another comment
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies' # 👉 related_name = name used to access reverse data
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # receiver
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notification")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)

    message = models.CharField(max_length=100)
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
    