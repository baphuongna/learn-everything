from django.contrib import admin
from .models import FlashcardSet, Flashcard, SpacedRepetitionSchedule

class FlashcardInline(admin.TabularInline):
    model = Flashcard
    extra = 1

@admin.register(FlashcardSet)
class FlashcardSetAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'created_at', 'updated_at')
    list_filter = ('lesson__topic__subject', 'lesson__topic')
    search_fields = ('title', 'description')
    inlines = [FlashcardInline]

@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('front', 'flashcard_set', 'created_at', 'updated_at')
    list_filter = ('flashcard_set__lesson__topic__subject', 'flashcard_set')
    search_fields = ('front', 'back')

@admin.register(SpacedRepetitionSchedule)
class SpacedRepetitionScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'flashcard', 'recall_level', 'next_review_date', 'review_count')
    list_filter = ('user', 'recall_level', 'next_review_date')
    search_fields = ('user__username', 'flashcard__front')
    date_hierarchy = 'next_review_date'
