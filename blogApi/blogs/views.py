from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated,AllowAny, IsAdminUser
from blogApi.blogs.serializers import UserSerializer, BlogUserSerializer, BlogPostSerializer, LikeSerializer
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import action
from rest_framework.validators import UniqueValidator
from .models import BlogUser, BlogPost,PostLikes
from rest_framework.response import Response
from blogApi.blogs.permissions import IsOwnerOrReadOnly, hasPermissionToUpdateProfile, hasPermissionToUpdateBlog
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
    
        if self.action in ['list','retrieve'] :
            permission_classes = [IsAdminUser]
        elif self.action in ['update','partial_update','destroy']:
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
        else:
            return Response(serializer.errors)
        
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = UserSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT,headers = {"detail":"User successfully deleted"})
        
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        BlogUser.objects.create(user=instance)



class BlogUserViewset(viewsets.ModelViewSet):
    queryset = BlogUser.objects.all()
    serializer_class = BlogUserSerializer

    def get_permissions(self):
    
        if self.action in ['list','create','retrieve']:
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

    def retrieve(self, request, pk=None):
        try:
            queryset = BlogUser.objects.all()
            user = get_object_or_404(queryset, pk=pk)
            serializer = BlogUserSerializer(user)
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
            else:
                return Response(serializer.errors)
    
    
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


class BlogPostViewset(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all().order_by('-date_created')
    serializer_class = BlogPostSerializer

    def get_permissions(self):
    
        if self.action in ['list','create','retrieve']:
            permission_classes = [IsAuthenticated]
        
        elif self.action in ['update','destroy','partial_update']:
            permission_classes = [IsAuthenticated,hasPermissionToUpdateBlog]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def list(self, request):
        
        try:
            queryset = BlogPost.objects.all().order_by('-date_created')
            serializer = BlogPostSerializer(queryset, many=True)
            return Response(serializer.data)
        except:
            return Response("Cannot make a request without authenication")

    def create(self, request):
        # blogUserInstance = BlogUser.objects.all()
        # if blogUserInstance.filter(user=request.user).exists():
        #     return Response({'detail':'Profile already exists'})
        # else:
        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
    
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_200_OK,data= {"detail":"Blog successfully deleted"})


    def perform_create(self, serializer):
        #print(self.request.user)
        currentuser = Token.objects.get(key=self.request.auth).user
        serializer.save(author=currentuser)


class CreateLikesView(APIView):
    """
    Create a like instance
    """
    permission_classes = [IsAuthenticated]
    def get_object(self, postId):
        try:
            return BlogPost.objects.get(id=postId)
        except BlogPost.DoesNotExist:
            raise Http404

    def post(self, request, postId, format=None):
        print(postId)
        data = request.data
        # user = request.user
        currentuser = Token.objects.get(key=self.request.auth).user
        blogpost = self.get_object(postId)
        existuserlike = [like for like in blogpost.likes.all() if like.user.pk == currentuser.pk]
        if (existuserlike):
            return Response('You have already liked this post')
        else:
            # data['user'] = currentuser.pk
            data['blog'] = blogpost.pk
            serializer = LikeSerializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)
                newlike = serializer.save()
                print("hello", newlike)
                blogpost.likes.add(newlike)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        #print(self.request.user)
        currentuser = Token.objects.get(key=self.request.auth).user
        serializer.save(user=currentuser)

class DeleteLikesView(APIView):
    """
    Create a like instance
    """
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return PostLikes.objects.get(pk=pk)
        except PostLikes.DoesNotExist:
            raise Http404

    def delete(self, request, pk, format=None):
        postlike = self.get_object(pk)
        postlike.delete()
        # return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_200_OK, data={"detail": "Blog successfully deleted"})
        

class AddFollowView(APIView):
    permission_classes = [IsAuthenticated]
    # def get_object(self, username):
    #     try:
    #         return BlogUser.objects.get(user.username = username)
    #     except BlogUser.DoesNotExist:
    #         raise Http404

    def post(self, request, followname, format=None):
       
        logged_in_user = Token.objects.get(key=self.request.auth).user
        # followname = kwargs['followname']
        logged_in_bloguser = BlogUser.objects.get(user=logged_in_user)
        newfollow = User.objects.get(username=followname)
        newfollowBlogUser = BlogUser.objects.get(user=newfollow)
        existingFollower = [follower for follower in logged_in_bloguser.following.all() if follower.user.username == followname]
        if (existingFollower):
            return Response('Already a follower')
        else:
            logged_in_bloguser.following.add(newfollowBlogUser)
            serializer = BlogUserSerializer(newfollowBlogUser)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class RemoveFollowView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, followname, format=None):
        logged_in_user = Token.objects.get(key=self.request.auth).user
        # followname = kwargs['followname']
        logged_in_bloguser = BlogUser.objects.get(user=logged_in_user)
        newfollow = User.objects.get(username=followname)
        newfollowBlogUser = BlogUser.objects.get(user=newfollow)
        existingFollower = [follower for follower in logged_in_bloguser.following.all() if follower.user.username == followname]
        print(existingFollower)
        if (not existingFollower):
            return Response('No follower to be deleted')
        else:
            logged_in_bloguser.following.remove(newfollowBlogUser)
            serializer = BlogUserSerializer(newfollowBlogUser)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
