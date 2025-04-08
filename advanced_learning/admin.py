from django.contrib import admin
from .models import (
    Project, ProjectTask, UserProject,
    InteractiveExercise,
    CornellNote,
    FeynmanNote,
    MindMap,
    PomodoroSession,
    CompetitionMode, CompetitionQuestion, CompetitionAnswer, CompetitionParticipant
)

# Hệ thống học tập dựa trên dự án
class ProjectTaskInline(admin.TabularInline):
    model = ProjectTask
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'difficulty_level', 'estimated_hours', 'created_at')
    list_filter = ('subject', 'difficulty_level')
    search_fields = ('title', 'description')
    inlines = [ProjectTaskInline]

@admin.register(UserProject)
class UserProjectAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'status', 'progress', 'started_at', 'completed_at')
    list_filter = ('status', 'project__subject')
    search_fields = ('user__username', 'project__title')

# Bài tập thực hành tương tác
@admin.register(InteractiveExercise)
class InteractiveExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'exercise_type', 'created_at')
    list_filter = ('exercise_type', 'lesson__topic__subject')
    search_fields = ('title', 'description', 'content')

# Hệ thống ghi chú Cornell
@admin.register(CornellNote)
class CornellNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'subject', 'created_at')
    list_filter = ('subject',)
    search_fields = ('title', 'main_notes', 'cue_column', 'summary')

# Phương pháp Feynman Technique
@admin.register(FeynmanNote)
class FeynmanNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'subject', 'created_at')
    list_filter = ('subject',)
    search_fields = ('title', 'concept', 'explanation', 'refined_explanation')

# Hệ thống Mind Mapping
@admin.register(MindMap)
class MindMapAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'subject', 'central_topic', 'created_at')
    list_filter = ('subject',)
    search_fields = ('title', 'central_topic')

# Pomodoro Timer
@admin.register(PomodoroSession)
class PomodoroSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'start_time', 'end_time', 'completed_pomodoros')
    list_filter = ('subject',)
    search_fields = ('user__username', 'notes')

# Chế độ thi đấu
class CompetitionQuestionInline(admin.TabularInline):
    model = CompetitionQuestion
    extra = 1

class CompetitionAnswerInline(admin.TabularInline):
    model = CompetitionAnswer
    extra = 2

@admin.register(CompetitionMode)
class CompetitionModeAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'start_time', 'end_time', 'time_limit', 'is_active')
    list_filter = ('subject', 'is_active')
    search_fields = ('title', 'description')
    inlines = [CompetitionQuestionInline]

@admin.register(CompetitionQuestion)
class CompetitionQuestionAdmin(admin.ModelAdmin):
    list_display = ('competition', 'question_text', 'points', 'order')
    list_filter = ('competition',)
    search_fields = ('question_text',)
    inlines = [CompetitionAnswerInline]

@admin.register(CompetitionParticipant)
class CompetitionParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'competition', 'score', 'rank', 'start_time', 'end_time')
    list_filter = ('competition',)
    search_fields = ('user__username',)
