from django.contrib import admin
from .models import SpeechRecognitionResult


@admin.register(SpeechRecognitionResult)
class SpeechRecognitionResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'text_result_preview')
    list_filter = ('created_at', 'user')
    search_fields = ('text_result', 'user__username')
    readonly_fields = ('created_at',)
    
    def text_result_preview(self, obj):
        if len(obj.text_result) > 50:
            return f"{obj.text_result[:50]}..."
        return obj.text_result
    
    text_result_preview.short_description = 'Kết quả nhận diện'
