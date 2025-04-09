"""
Forms cho ứng dụng flashcards.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import FlashcardSet, Flashcard
from content.models import Lesson, Subject, Topic

class FlashcardSetForm(forms.ModelForm):
    """Form tạo và chỉnh sửa bộ flashcard."""
    
    class Meta:
        model = FlashcardSet
        fields = ['title', 'description', 'lesson']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tiêu đề bộ flashcard'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mô tả bộ flashcard'}),
            'lesson': forms.Select(attrs={'class': 'form-select'})
        }

class FlashcardForm(forms.ModelForm):
    """Form tạo và chỉnh sửa flashcard."""
    
    class Meta:
        model = Flashcard
        fields = ['front', 'back', 'image', 'order']
        widgets = {
            'front': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Mặt trước flashcard'}),
            'back': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Mặt sau flashcard'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0})
        }

class AutoGenerateFlashcardsForm(forms.Form):
    """Form tự động tạo flashcards từ bài học."""
    
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'hx-get': '/flashcards/get-topics/', 'hx-target': '#id_topic', 'hx-trigger': 'change'}),
        label=_('Chủ đề')
    )
    
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select', 'hx-get': '/flashcards/get-lessons/', 'hx-target': '#id_lesson', 'hx-trigger': 'change'}),
        label=_('Chủ đề con')
    )
    
    lesson = forms.ModelChoiceField(
        queryset=Lesson.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Bài học')
    )
    
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tiêu đề bộ flashcard'}),
        label=_('Tiêu đề')
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mô tả bộ flashcard'}),
        label=_('Mô tả')
    )
    
    max_cards = forms.IntegerField(
        min_value=1,
        max_value=50,
        initial=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 50}),
        label=_('Số lượng flashcard tối đa')
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
