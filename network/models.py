from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
        }
    
    def is_liked_by(self, user):
        return self.liked.filter(user=user).exists()

    def __str__(self):
        return f"{self.user} posted {self.content} on {self.timestamp}"
    

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed")

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'following'], name='unique_user_following')
        ]

    def __str__(self):
        return f"{self.user} follows {self.following}"
    
    def serialize(self):
        return {
            "user": self.user.username,
            "following": self.following.username
        }

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liker")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="liked")

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'post'], name='unique_user_post')
        ]

    def __str__(self):
        return f"{self.user} likes {self.post}"

    def serialize(self):
        return {
            "user": self.user.username,
            "post": self.post.id
        }


