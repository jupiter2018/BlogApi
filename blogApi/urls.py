from django.urls import include, path
from rest_framework import routers
from blogApi.blogs import views
from django.contrib import admin
from rest_framework.authtoken.views import obtain_auth_token
from blogApi.blogs.models import BlogUser,BlogPost,PostLikes
admin.site.register(BlogUser)
admin.site.register(BlogPost)
admin.site.register(PostLikes)
router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('profile', views.BlogUserViewset)
router.register('blogposts',views.BlogPostViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('postlikes/<int:postId>/', views.CreateLikesView.as_view()),
    path('deletelikes/<int:pk>/',views.DeleteLikesView.as_view()),
    path('admin/', admin.site.urls),
       
]

urlpatterns += [
     path('api-token-auth/', obtain_auth_token),
] 