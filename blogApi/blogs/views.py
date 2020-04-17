from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated,AllowAny
from blogApi.blogs.serializers import UserSerializer, BlogUserSerializer
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import action
from rest_framework.validators import UniqueValidator
from .models import BlogUser
from rest_framework.response import Response
from blogApi.blogs.permissions import IsOwnerOrReadOnly, hasPermissionToUpdateProfile

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
    
        if self.action in ['list'] :
            permission_classes = [IsAuthenticated]
        elif self.action in ['update','partial_update']:
            permission_classes = [IsAuthenticated,
                      IsOwnerOrReadOnly]    
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def list(self, request):
        try:
            queryset = User.objects.all()
            serializer = UserSerializer(queryset, many=True)
            return Response(serializer.data)
        except:
            return Response("Cannot make a request without authenication")

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = UserSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
        
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class BlogUserViewset(viewsets.ModelViewSet):
    queryset = BlogUser.objects.all()
    serializer_class = BlogUserSerializer

    def get_permissions(self):
    
        if self.action in ['list','create']:
            permission_classes = [IsAuthenticated]
        
        elif self.action in ['update','destroy','partial_update']:
            permission_classes = [IsAuthenticated,hasPermissionToUpdateProfile]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def list(self, request):
        
        try:
            queryset = BlogUser.objects.all()
            serializer = BlogUserSerializer(queryset, many=True)
            return Response(serializer.data)
        except:
            return Response("Cannot make a request without authenication")

    def create(self, request):
        blogUserInstance = BlogUser.objects.all()
        if blogUserInstance.filter(user=request.user).exists():
            return Response({'detail':'Profile already exists'})
        else:
            serializer = BlogUserSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                self.perform_create(serializer)
                serializer.save()
                return Response(serializer.data)
    
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


    def perform_create(self, serializer):
        #print(self.request.user)
        currentuser = Token.objects.get(key=self.request.auth).user
        serializer.save(user=currentuser)

    # def perform_update(self, serializer):
    #     currentuser = Token.objects.get(key=self.request.auth).user
    #     serializer.save(user=currentuser)
