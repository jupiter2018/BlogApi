from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class BlogUser(models.Model):
     user = models.OneToOneField(User,on_delete=models.CASCADE)
     following = models.ManyToManyField("self", blank=True, symmetrical=False)
     body = models.TextField(max_length=1000, blank=True)
     def __str__(self):
        return f"{self.user}-{self.following}"


class BlogPost(models.Model):
   title = models.CharField(max_length=50, null=False, blank=False)
   body = models.TextField(max_length=2000, blank=False, null=False)
   date_created = models.DateTimeField(auto_now_add=True, verbose_name='date created')
   date_updated = models.DateTimeField(auto_now=True, verbose_name='date updated')
   likes = models.ManyToManyField('PostLikes',blank=True)
   author = models.ForeignKey(User, on_delete=models.CASCADE)
   def __str__(self):
        return f"{self.author.username}-{self.title}"

class PostLikes(models.Model):
   user = models.ForeignKey(User,on_delete=models.CASCADE)
   blogpost = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
   created = models.DateTimeField(auto_now_add=True)