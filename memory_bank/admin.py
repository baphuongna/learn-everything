from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import MemoryCategory, MemoryItem, MemoryAttachment

class MemoryAttachmentInline(admin.TabularInline):
    model = MemoryAttachment
    extra = 1

@admin.register(MemoryCategory)
class MemoryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'subject', 'created_at', 'updated_at')
    list_filter = ('user', 'subject')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(MemoryItem)
class MemoryItemAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ('title', 'user', 'category', 'priority', 'is_favorite', 'created_at', 'updated_at')
    list_filter = ('user', 'category', 'priority', 'is_favorite')
    search_fields = ('title', 'content', 'tags')
    inlines = [MemoryAttachmentInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(MemoryAttachment)
class MemoryAttachmentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'memory_item', 'file_type', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('file_name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(memory_item__user=request.user)