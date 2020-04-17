from django.urls import include, path
from rest_framework import routers
from blogApi.blogs import views
from django.contrib import admin
from rest_framework.authtoken.views import obtain_auth_token
from blogApi.blogs.models import BlogUser

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('profile', views.BlogUserViewset)
admin.site.register(BlogUser)
# router.register('login',views.LoginViewSet)
#router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    
    
]

urlpatterns += [
     path('api-token-auth/', obtain_auth_token),
] 