from django.contrib import admin
from .models import (
    LearningPathway, PathwayStep, LearningPreference, ContentRecommendation,
    UserInteraction, UserStrengthWeakness, UIPreference, StudyReminder
)

class PathwayStepInline(admin.TabularInline):
    model = PathwayStep
    extra = 1

@admin.register(LearningPathway)
class LearningPathwayAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'subject', 'difficulty_level', 'is_active', 'created_at')
    list_filter = ('difficulty_level', 'is_active', 'subject')
    search_fields = ('title', 'description', 'user__username')
    inlines = [PathwayStepInline]

@admin.register(PathwayStep)
class PathwayStepAdmin(admin.ModelAdmin):
    list_display = ('title', 'pathway', 'step_type', 'order', 'is_completed', 'completed_at')
    list_filter = ('step_type', 'is_completed')
    search_fields = ('title', 'description', 'pathway__title')

@admin.register(LearningPreference)
class LearningPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_learning_style', 'preferred_difficulty', 'preferred_study_time')
    list_filter = ('preferred_learning_style', 'preferred_difficulty')
    search_fields = ('user__username',)
    filter_horizontal = ('preferred_topics',)

@admin.register(ContentRecommendation)
class ContentRecommendationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'recommendation_type', 'subject', 'relevance_score', 'is_viewed', 'is_helpful')
    list_filter = ('recommendation_type', 'is_viewed', 'is_helpful', 'subject')
    search_fields = ('title', 'description', 'user__username')

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'interaction_type', 'content_type', 'content_id', 'rating', 'interaction_time')
    list_filter = ('interaction_type', 'content_type')
    search_fields = ('user__username',)

@admin.register(UserStrengthWeakness)
class UserStrengthWeaknessAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'topic', 'is_strength', 'proficiency_score', 'last_assessment_date')
    list_filter = ('is_strength', 'subject')
    search_fields = ('user__username', 'notes')

@admin.register(UIPreference)
class UIPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'color_theme', 'font_size', 'enable_animations', 'updated_at')
    list_filter = ('color_theme', 'font_size', 'enable_animations')
    search_fields = ('user__username',)

@admin.register(StudyReminder)
class StudyReminderAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'reminder_type', 'notification_method', 'reminder_time', 'is_active', 'last_sent')
    list_filter = ('reminder_type', 'notification_method', 'is_active')
    search_fields = ('title', 'message', 'user__username')
