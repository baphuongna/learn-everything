"""
Forms cho ứng dụng ai_assistant.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from content.models import Subject, Topic, Lesson
from .models import AIAssistantChat, AIAssistantMessage, AIAssistantFeedback, AIAssistantPrompt

class AIAssistantMessageForm(forms.Form):
    """Form gửi tin nhắn cho trợ lý AI."""
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Nhập câu hỏi của bạn...',
            'autofocus': 'autofocus'
        }),
        label=_('Tin nhắn')
    )

class AIAssistantChatForm(forms.Form):
    """Form tạo cuộc trò chuyện mới với trợ lý AI."""
    
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'hx-get': '/ai-assistant/get-topics/',
            'hx-target': '#id_topic',
            'hx-trigger': 'change'
        }),
        label=_('Chủ đề'),
        required=False
    )
    
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'hx-get': '/ai-assistant/get-lessons/',
            'hx-target': '#id_lesson',
            'hx-trigger': 'change'
        }),
        label=_('Chủ đề con'),
        required=False
    )
    
    lesson = forms.ModelChoiceField(
        queryset=Lesson.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Bài học'),
        required=False
    )
    
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tiêu đề cuộc trò chuyện'
        }),
        label=_('Tiêu đề'),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Nếu đã chọn chủ đề, lọc danh sách chủ đề con
        if 'subject' in self.data:
            try:
                subject_id = int(self.data.get('subject'))
                self.fields['topic'].queryset = Topic.objects.filter(subject_id=subject_id).order_by('order')
            except (ValueError, TypeError):
                pass
        
        # Nếu đã chọn chủ đề con, lọc danh sách bài học
        if 'topic' in self.data:
            try:
                topic_id = int(self.data.get('topic'))
                self.fields['lesson'].queryset = Lesson.objects.filter(topic_id=topic_id).order_by('order')
            except (ValueError, TypeError):
                pass

class AIAssistantFeedbackForm(forms.ModelForm):
    """Form gửi phản hồi về câu trả lời của trợ lý AI."""
    
    class Meta:
        model = AIAssistantFeedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'rating-input'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Nhập nhận xét của bạn...'
            })
        }

class AIAssistantPromptForm(forms.ModelForm):
    """Form tạo và chỉnh sửa prompt cho trợ lý AI."""
    
    class Meta:
        model = AIAssistantPrompt
        fields = ['name', 'prompt_type', 'content', 'subject', 'topic', 'lesson', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'prompt_type': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'topic': forms.Select(attrs={'class': 'form-select'}),
            'lesson': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
