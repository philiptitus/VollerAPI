from rest_framework import serializers
from .models import CustomUser as Userr
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
import json
from dataclasses import field
from rest_framework import serializers
from string import ascii_lowercase, ascii_uppercase
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import *
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import serializers
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from .utils import send_normal_email





class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)
    bio = serializers.SerializerMethodField(read_only=True)
    date_joined = serializers.SerializerMethodField(read_only=True)



    




    class Meta:
        model = Userr
        fields = '__all__'


    def get__id(self, obj):
        return obj.id
    
    def get_isAdmin(self, obj):
        return obj.is_staff

        
    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email

        return name
    
    def get_bio(self, obj):
        bio = obj.bio


        return bio
    
    def get_avi(self, obj):
        avi = obj.avi


        return avi


    def get_date_joined(self, obj):
        date_joined = obj.date_joined


        return date_joined
    

# class NotificationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Notification
#         fields = ['id', 'message', 'read', 'timestamp']
    



class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Userr
        fields = ['id', '_id', 'username', 'email', 'name', 'isAdmin', 'bio', 'token', 'date_joined']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)
    


import os


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    template_path = os.path.join(settings.BASE_DIR, 'base', 'email_templates', 'Confirm.html')
    with open(template_path, 'r', encoding='utf-8') as template_file:
        html_content = template_file.read()


    def validate(self, attrs):
        email = attrs.get('email')
        if Userr.objects.filter(email=email).exists():
            user = Userr.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request = self.context.get('request')
            abslink = f"https://jennie-steel.vercel.app/auth/password-reset-confirm/{uidb64}/{token}/"
            print(abslink)
            email_body = f"Hi {user.first_name}, use the link below to reset your password: {abslink} Hurry Up The Link Expires in Two Minutes"
            
            
            template_path = os.path.join(settings.BASE_DIR, 'base', 'email_templates', 'Confirm.html')
            with open(template_path, 'r', encoding='utf-8') as template_file:
                html_content = template_file.read()             
            data = {
                'email_body': html_content,
                'email_subject': "Reset your Password",
                'to_email': user.email,
                'context': {
                    'name': user.first_name,
                    'link': abslink,
                },
            }
            send_normal_email(data)

        return super().validate(attrs)
    

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
import os
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)
    token = serializers.CharField(min_length=3, write_only=True)

    class Meta:
        fields = ['password', 'confirm_password', 'uidb64', 'token']

    def validate(self, attrs):
        try:
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            password = attrs.get('password')
            confirm_password = attrs.get('confirm_password')

            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = Userr.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("Reset link is invalid or has expired", 401)

            if password != confirm_password:
                raise AuthenticationFailed("Passwords do not match")

            # Validate password using Django's password validators
            try:
                validate_password(password, user)
            except ValidationError as e:
                raise ValidationError(detail=str(e))

            user.set_password(password)
            user.save()


            template_path = os.path.join(settings.BASE_DIR, 'base', 'email_templates', 'Success.html')
            with open(template_path, 'r', encoding='utf-8') as template_file:
                html_content = template_file.read()

            # Send email notifying the user of the password change
            email_body = f"Hi {user.first_name}, your password For GALLERY has been successfully changed If This Was Not You Change It Back Immediately."
            email_subject = "Password Change Notification"
            to_email = user.email
            data = {
                'email_body': html_content,
                'email_subject': email_subject,
                'to_email': to_email,
                'context': {
                    'name': user.first_name,
                },
            }
            send_normal_email(data)

            return user
        except Exception as e:
            raise AuthenticationFailed("Link is invalid or has expired")

















class TrendingIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendingIssue
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

class InstagramDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramData
        fields = '__all__'

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = '__all__'

class FactCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactCheck
        fields = '__all__'

class CourseBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseBlock
        fields = '__all__'

class GoogleSearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleSearchResult
        fields = '__all__'

class YouTubeLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeLink
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class AsisstantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asisstant
        fields = '__all__'





class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()  # To include nested replies

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'parent', 'replies']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return None

class FinanceSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)  # To show all comments related to the finance object

    class Meta:
        model = Finance
        fields = ['id', 'title', 'location', 'amount', 'last_updated', 'description', 'processed', 'comment_count', 'comments']
