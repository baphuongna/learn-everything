from django.contrib import admin
from .models import Quiz, Question, Answer, QuizAttempt, UserAnswer

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'time_limit', 'pass_score', 'created_at', 'updated_at')
    list_filter = ('lesson__topic__subject', 'lesson__topic')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quiz', 'question_type', 'order')
    list_filter = ('quiz', 'question_type')
    search_fields = ('question_text', 'explanation')
    inlines = [AnswerInline]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('answer_text', 'question', 'is_correct')
    list_filter = ('question__quiz', 'is_correct')
    search_fields = ('answer_text',)

class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0
    readonly_fields = ('question', 'selected_answers', 'text_answer', 'is_correct')
    can_delete = False

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'passed', 'start_time', 'end_time', 'created_at')
    list_filter = ('user', 'quiz', 'passed')
    search_fields = ('user__username', 'quiz__title')
    readonly_fields = ('user', 'quiz', 'score', 'passed', 'start_time', 'end_time')
    inlines = [UserAnswerInline]

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('quiz_attempt', 'question', 'is_correct', 'created_at')
    list_filter = ('quiz_attempt__quiz', 'is_correct')
    search_fields = ('quiz_attempt__user__username', 'question__question_text')
    readonly_fields = ('quiz_attempt', 'question', 'selected_answers', 'text_answer', 'is_correct')
