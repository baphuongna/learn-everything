from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UserProgress, StudySession

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Hồ sơ người dùng'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'completion_date', 'last_accessed')
    list_filter = ('user', 'completed', 'lesson__topic__subject')
    search_fields = ('user__username', 'lesson__title')
    date_hierarchy = 'last_accessed'

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'start_time', 'end_time', 'duration_minutes')
    list_filter = ('user', 'subject', 'start_time')
    search_fields = ('user__username', 'notes')
    date_hierarchy = 'start_time'
