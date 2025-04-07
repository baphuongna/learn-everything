from django.contrib import admin
from .models import Subject, Topic, Lesson

class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [TopicInline]

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'slug', 'order', 'created_at', 'updated_at')
    list_filter = ('subject',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'slug', 'order', 'created_at', 'updated_at')
    list_filter = ('topic__subject', 'topic')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
