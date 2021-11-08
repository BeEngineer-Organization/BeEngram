from django.contrib.auth.models import AbstractUser
from django.db import models
from django.templatetags.static import static


class User(AbstractUser):
    username = models.CharField("ユーザー名", max_length=20, unique=True)
    email = models.EmailField("メールアドレス", unique=True)
    profile = models.CharField(max_length=150)
    follow = models.ManyToManyField("User", related_name="followed")
    icon = models.ImageField(upload_to="icons/", blank=True)
    like = models.ManyToManyField("Post", related_name="liked_users")

    def __str__(self):
        return self.username

    @property
    def icon_url(self):
        if self.icon:
            return self.icon.url
        return static("main/img/default-icon.svg")


class Post(models.Model):
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="posts"
    )
    img = models.ImageField(upload_to="posts/")
    note = models.CharField(max_length=300, blank=True)
    post_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} : {self.post_date}"


class Comment(models.Model):
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="comments"
    )
    post = models.ForeignKey(
        "Post", on_delete=models.CASCADE, related_name="comments"
    )
    text = models.CharField(max_length=150)
    post_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → ({self.post}) : {self.post_date}"
