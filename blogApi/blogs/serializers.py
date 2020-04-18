
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from .models import BlogUser, BlogPost, PostLikes


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    username = serializers.CharField(
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(min_length=8,style={'input_type':'password'},write_only=True)
    password2 = serializers.CharField(min_length=8,write_only=True,style={'input_type':'password'})

    def create(self, validated_data):
        
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'passwords must match'})
        else:
            user = User.objects.create_user(validated_data['username'], validated_data['email'],
             validated_data['password'])
            
            return user

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password','password2')


class BlogUserSerializer(serializers.ModelSerializer):
    # user_email = serializers.EmailField(required=False,
    #         validators=[UniqueValidator(queryset=User.objects.all())],write_only=True
    #         )
    password = serializers.CharField(required=False,min_length=8,style={'input_type':'password'},write_only=True)
    class Meta:
        model = BlogUser
        fields = ('id', 'username', 'email', 'body', 'password', 'following')
        depth=1
        #user = serializers.ReadOnlyField(source='user.username')
    username = serializers.SerializerMethodField('get_username')
    email = serializers.SerializerMethodField('get_email')
    #password = serializers.SerializerMethodField('get_password')
    #user = serializers.ReadOnlyField(source='user.username')
    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email
    
    def create(self, validated_data):
        print(validated_data)
        return BlogUser.objects.create(**validated_data)

    
    
class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ('id', 'username', 'title', 'body', 'date_created', 'date_updated','likes')
    username = serializers.SerializerMethodField('get_username')

    def get_username(self, obj):
        return obj.author.username

class LikeSerializer(serializers.ModelSerializer):
   class Meta:
       model = PostLikes
       fields = ('user', 'blogpost', 'created')