from django.contrib import admin

# Register your models here.
from blogs.models import BlogUser, BlogPost, PostLikes
admin.site.register(BlogUser)
admin.site.register(BlogPost)
admin.site.register(PostLikes)
