from django.db import models

from django.contrib.auth.models import User

class BlogUser(models.Model):
     user = models.OneToOneField(User,on_delete=models.CASCADE)
     following = models.ManyToManyField("self", blank=True, symmetrical=False)
     body = models.TextField(max_length=1000, blank=True)
     def __str__(self):
        return f"{self.user}-{self.following}"