from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    generated_text = models.TextField()
    summary_text = models.TextField()
    summary_keywords=models.TextField(null=True)
    summary_title= models.CharField(max_length=250,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Summary for {self.user.username} at {self.created_at}"