from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission
from django.conf import settings
# Create your models here.
from django.utils import timezone


# TrendingIssue model for storing trending issues with locations
class TrendingIssue(models.Model):
    issue = models.CharField(max_length=500)
    location = models.CharField(max_length=255)
    count = models.PositiveIntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)
    description = models.TextField()
    processed = models.BooleanField(default=False)



    
    def __str__(self):
        return self.issue

# Course model for storing virtual classroom courses
class Course(models.Model):
    issue = models.ForeignKey(TrendingIssue, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    ready = models.BooleanField(default=False)
    description = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    capacity = models.PositiveIntegerField(default = 0)

    
    def __str__(self):
        return self.title





class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)




AUTH_PROVIDERS = {'email': 'email', 'google': 'google', 'github': 'github', 'linkedin': 'linkedin'}

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    avi = models.ImageField(null=True, blank=True, default='/avatar.png')
    isPrivate = models.BooleanField(default=False)
    auth_provider = models.CharField(max_length=50, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)

    # Adding the credits field with a default value of 1000
    credits = models.IntegerField(default=1000)

    # Adding the requested integer fields with default values of 0
    tjobs = models.IntegerField(default=0)
    usessions = models.IntegerField(default=0)
    csessions = models.IntegerField(default=0)
    passed = models.IntegerField(default=0)
    failed = models.IntegerField(default=0)

    objects = CustomUserManager()
    user_permissions = models.ManyToManyField(Permission, verbose_name='user permissions', blank=True)

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.email
    
    def tokens(self):    
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }





from django.db import models

# News model for storing articles pulled from the News API
class News(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField()
    url = models.URLField()
    published_at = models.DateTimeField()
    
    def __str__(self):
        return self.title

# Instagram data model for storing posts pulled from Instagram Graph API
class InstagramData(models.Model):
    special_id = models.TextField(blank=True, null=True)
    caption = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    first_analysis = models.BooleanField(default=False)
    second_analysis = models.BooleanField(default=False)
    p_analysis = models.BooleanField(default=False)
    p_analysis2 = models.BooleanField(default=False)
    f_analysis = models.BooleanField(default=False)
    f_analysis2 = models.BooleanField(default=False)






    def __str__(self):
        return f"{self.special_id[:30]}"



class Prediction(models.Model):
    JOB_SHORTAGE = 'job_shortage'
    CIVIL_UNREST = 'civil_unrest'
    ECONOMIC_CRISIS = 'economic_crisis'
    CLIMATE_RISK = 'climate_risk'
    MISINFORMATION = 'misinformation'
    MENTAL_HEALTH = 'mental_health'
    HUMAN_RIGHTS = 'human_rights'
    YOUTH_UNEMPLOYMENT = 'youth_unemployment'
    GENERAL = 'general'
    
    PREDICTION_TYPE_CHOICES = [
        (JOB_SHORTAGE, 'Job Shortage'),
        (CIVIL_UNREST, 'civil_unrest'),
        (ECONOMIC_CRISIS, 'Economic Crisis'),
        (CLIMATE_RISK, 'Climate Risk'),
        (MISINFORMATION, 'Misinformation Spread'),
        (MENTAL_HEALTH, 'Mental Health Crisis'),
        (HUMAN_RIGHTS, 'Human Rights Violations'),
        (YOUTH_UNEMPLOYMENT, 'Youth Unemployment'),
        (GENERAL, 'General'),
    ]
    
    title = models.CharField(max_length=500)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True, null=True)
    predicted_at = models.DateTimeField(auto_now_add=True)
    count = models.PositiveIntegerField(default=1)
    processed = models.BooleanField(default=False)
    type = models.CharField(
        max_length=50,
        choices=PREDICTION_TYPE_CHOICES,
        default=GENERAL
    )
    
    def __str__(self):
        return f"Prediction: {self.title[:50]}"


# FactCheck model for storing user-submitted data for fact-checking
class FactCheck(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    submitted_data = models.TextField()
    fact_checked = models.BooleanField(default=False)
    verdict = models.CharField(max_length=50, blank=True, null=True)
    


class CourseBlock(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='blocks')
    question = models.TextField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    my_answer = models.TextField(blank=True, null=True)
    attempted = models.BooleanField(default=False)
    score = models.FloatField(default=0)  # New field for the score of each block

    # def __str__(self):
    #     return f"{self.id()} Block for {self.preparation_material.title}"



class GoogleSearchResult(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='searches')
    title = models.CharField(max_length=255)
    snippet = models.TextField()
    link = models.URLField()
    attempted = models.BooleanField(default=False)


    def __str__(self):
        return self.title
    



class YouTubeLink(models.Model):
    preparation_material = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='youtube')
    title = models.CharField(max_length=255)
    embed_url = models.URLField()
    attempted = models.BooleanField(default=False)


    def __str__(self):
        return self.title




class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} at {self.timestamp}"



class Asisstant(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='asisstant')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.TextField()
    question = models.TextField()
    response = models.TextField()
    last_interaction = models.DateTimeField(blank=True, null=True)
    ready = models.BooleanField(default=False)


    def __str__(self):
        return f"Assistant response for session {self.session.id}"









from django.db import models
from django.conf import settings

class Finance(models.Model):
    title = models.CharField(max_length=500)
    location = models.CharField(max_length=255)
    amount = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    description = models.TextField()
    processed = models.BooleanField(default=False)
    comment_count = models.PositiveIntegerField(default=0)  # Field to track the number of comments

    def __str__(self):
        return self.title

class Comment(models.Model):
    finance = models.ForeignKey(Finance, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f"Comment by {self.user.email} on {self.finance.title}"
