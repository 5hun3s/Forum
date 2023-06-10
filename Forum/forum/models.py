from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Forum(models.Model):
    title = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.title)+"-year:"+str(self.created_at.year)+"-month:"+str(self.created_at.month)+"-day:"+str(self.created_at.day)

class Comment(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    text = models.TextField()
    #response = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.user)+"-year:"+str(self.created_at.year)+"-month:"+str(self.created_at.month)+"-day:"+str(self.created_at.day)

