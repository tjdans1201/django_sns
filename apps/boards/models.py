from turtle import ondrag
from django.db import models
from ..users.models import User


class Board(models.Model):
    index = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    content = models.TextField()
    hashtag = models.CharField(max_length=50)
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    heart_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)


class Heart(models.Model):
    index = models.AutoField(primary_key=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


# Create your models here.
