"""
Forms cho ứng dụng quizzes.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Quiz, Question, Answer
from content.models import Lesson, Subject, Topic

class QuizForm(forms.ModelForm):
    """Form tạo và chỉnh sửa bài kiểm tra."""
    
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'lesson', 'time_limit', 'pass_score']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tiêu đề bài kiểm tra'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mô tả bài kiểm tra'}),
            'lesson': forms.Select(attrs={'class': 'form-select'}),
            'time_limit': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'pass_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100})
        }

class QuestionForm(forms.ModelForm):
    """Form tạo và chỉnh sửa câu hỏi."""
    
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'explanation', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Nội dung câu hỏi'}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Giải thích đáp án'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0})
        }

class AnswerForm(forms.ModelForm):
    """Form tạo và chỉnh sửa đáp án."""
    
    class Meta:
        model = Answer
        fields = ['answer_text', 'is_correct']
        widgets = {
            'answer_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 1, 'placeholder': 'Nội dung đáp án'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class AutoGenerateQuizForm(forms.Form):
    """Form tự động tạo bài kiểm tra từ bài học."""
    
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'hx-get': '/quizzes/get-topics/', 'hx-target': '#id_topic', 'hx-trigger': 'change'}),
        label=_('Chủ đề')
    )
    
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select', 'hx-get': '/quizzes/get-lessons/', 'hx-target': '#id_lesson', 'hx-trigger': 'change'}),
        label=_('Chủ đề con')
    )
    
    lesson = forms.ModelChoiceField(
        queryset=Lesson.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Bài học')
    )
    
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tiêu đề bài kiểm tra'}),
        label=_('Tiêu đề')
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mô tả bài kiểm tra'}),
        label=_('Mô tả')
    )
    
    num_questions = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
        label=_('Số lượng câu hỏi')
    )
    
    time_limit = forms.IntegerField(
        min_value=1,
        max_value=120,
        initial=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 120}),
        label=_('Thời gian làm bài (phút)')
    )
    
    pass_score = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=70,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        label=_('Điểm đậu (%)')
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
