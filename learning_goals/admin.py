from django.contrib import admin
from .models import LearningGoal, GoalProgress, GoalCollaborator, GoalComment, GoalInvitation

class GoalProgressInline(admin.TabularInline):
    model = GoalProgress
    extra = 0
    readonly_fields = ['date']

class GoalCollaboratorInline(admin.TabularInline):
    model = GoalCollaborator
    extra = 0

class GoalCommentInline(admin.TabularInline):
    model = GoalComment
    extra = 0
    readonly_fields = ['created_at', 'updated_at']

@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'goal_type', 'category', 'start_date', 'end_date', 'progress_percentage', 'status']
    list_filter = ['goal_type', 'category', 'status', 'start_date', 'end_date']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['progress_percentage', 'status', 'created_at', 'updated_at']
    fieldsets = [
        ('Thông tin cơ bản', {
            'fields': ['user', 'title', 'description']
        }),
        ('Phân loại', {
            'fields': ['goal_type', 'category']
        }),
        ('Thời gian', {
            'fields': ['start_date', 'end_date']
        }),
        ('Mục tiêu và tiến độ', {
            'fields': ['target_value', 'current_value', 'progress_percentage', 'status']
        }),
        ('Liên kết nội dung', {
            'fields': ['subject', 'topic', 'lesson'],
            'classes': ['collapse']
        }),
        ('Nhắc nhở', {
            'fields': ['reminder_enabled', 'reminder_frequency'],
            'classes': ['collapse']
        }),
        ('Phần thưởng', {
            'fields': ['reward_points', 'has_badge_reward', 'badge_name', 'badge_description', 'badge_level'],
            'classes': ['collapse']
        }),
        ('Chia sẻ', {
            'fields': ['is_public', 'allow_collaboration'],
            'classes': ['collapse']
        }),
        ('Thông tin hệ thống', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    inlines = [GoalProgressInline, GoalCollaboratorInline, GoalCommentInline]

@admin.register(GoalProgress)
class GoalProgressAdmin(admin.ModelAdmin):
    list_display = ['goal', 'date', 'value']
    list_filter = ['date', 'goal__goal_type', 'goal__category']
    search_fields = ['goal__title', 'notes']
    readonly_fields = ['goal']

@admin.register(GoalCollaborator)
class GoalCollaboratorAdmin(admin.ModelAdmin):
    list_display = ['goal', 'user', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['goal__title', 'user__username']

@admin.register(GoalComment)
class GoalCommentAdmin(admin.ModelAdmin):
    list_display = ['goal', 'user', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['goal__title', 'user__username', 'content']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(GoalInvitation)
class GoalInvitationAdmin(admin.ModelAdmin):
    list_display = ['goal', 'sender', 'recipient', 'role', 'status', 'created_at']
    list_filter = ['role', 'status', 'created_at']
    search_fields = ['goal__title', 'sender__username', 'recipient__username', 'message']
    readonly_fields = ['created_at', 'updated_at']
