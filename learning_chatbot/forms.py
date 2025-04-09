"""
Forms cho ứng dụng learning_chatbot.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ChatbotCategory, ChatbotQuestion, ChatbotFeedback

class ChatbotMessageForm(forms.Form):
    """Form gửi tin nhắn cho chatbot."""
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Nhập câu hỏi của bạn...',
            'autofocus': 'autofocus'
        }),
        label=_('Tin nhắn')
    )

class ChatbotFeedbackForm(forms.ModelForm):
    """Form gửi phản hồi về câu trả lời của chatbot."""
    
    class Meta:
        model = ChatbotFeedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'rating-input'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Nhận xét của bạn...'
            })
        }

class ChatbotCategoryForm(forms.ModelForm):
    """Form tạo và chỉnh sửa danh mục câu hỏi."""
    
    class Meta:
        model = ChatbotCategory
        fields = ['name', 'description', 'subject', 'topic', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'topic': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class ChatbotQuestionForm(forms.ModelForm):
    """Form tạo và chỉnh sửa câu hỏi."""
    
    class Meta:
        model = ChatbotQuestion
        fields = ['category', 'question', 'answer', 'keywords', 'lesson', 'order', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'question': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'keywords': forms.TextInput(attrs={'class': 'form-control'}),
            'lesson': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
