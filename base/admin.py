from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *



class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'auth_provider', 'is_staff', 'is_active', 'bio', "credits",'date_joined', 'avi', 'isPrivate')
    list_filter = ('email', 'username', 'is_staff', 'is_active', 'auth_provider',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('bio', 'date_joined', 'avi', "credits",'auth_provider',"tjobs","usessions","csessions","passed", "failed",)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions', 'isPrivate')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'isPrivate','user_permissions', 'bio', 'avi', 'auth_provider', "credits","tjobs","usessions","csessions","passed", "failed"),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    readonly_fields = ('date_joined',)  # Make date_joined non-editable


admin.site.register(TrendingIssue)
admin.site.register(Course)
admin.site.register(News)
admin.site.register(InstagramData)
admin.site.register(Prediction)
admin.site.register(FactCheck)
admin.site.register(CourseBlock)
admin.site.register(GoogleSearchResult)
admin.site.register(YouTubeLink)
admin.site.register(Notification)
admin.site.register(Asisstant)
admin.site.register(Finance)
