from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from content.models import Subject, Topic, Lesson
from .models import (
    LearningPathway, PathwayStep, LearningPreference, ContentRecommendation,
    UserInteraction, UserStrengthWeakness, UIPreference, StudyReminder
)

class LearningPathwayForm(forms.ModelForm):
    """Biểu mẫu tạo và chỉnh sửa lộ trình học tập"""
    class Meta:
        model = LearningPathway
        fields = ['title', 'description', 'subject', 'difficulty_level', 'estimated_duration_days']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class PathwayStepForm(forms.ModelForm):
    """Biểu mẫu tạo và chỉnh sửa bước trong lộ trình học tập"""
    class Meta:
        model = PathwayStep
        fields = ['title', 'description', 'step_type', 'order', 'lesson', 'external_content_url', 'estimated_duration_minutes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lọc bài học theo chủ đề của lộ trình nếu có
        if 'instance' in kwargs and kwargs['instance'] and kwargs['instance'].pathway:
            subject = kwargs['instance'].pathway.subject
            self.fields['lesson'].queryset = Lesson.objects.filter(topic__subject=subject)

class LearningPreferenceForm(forms.ModelForm):
    """Biểu mẫu sở thích học tập"""
    class Meta:
        model = LearningPreference
        fields = ['preferred_learning_style', 'preferred_difficulty', 'preferred_study_time', 
                 'preferred_session_duration', 'preferred_topics']
        widgets = {
            'preferred_study_time': forms.TimeInput(attrs={'type': 'time'}),
            'preferred_topics': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Lọc chủ đề theo sở thích của người dùng nếu có
        if user and hasattr(user, 'profile') and user.profile.preferred_subjects.exists():
            preferred_subjects = user.profile.preferred_subjects.all()
            self.fields['preferred_topics'].queryset = Topic.objects.filter(subject__in=preferred_subjects)

class UIPreferenceForm(forms.ModelForm):
    """Biểu mẫu tùy chỉnh giao diện"""
    class Meta:
        model = UIPreference
        fields = ['color_theme', 'font_size', 'enable_animations', 'sidebar_collapsed']
        widgets = {
            'color_theme': forms.RadioSelect(),
            'font_size': forms.RadioSelect(),
        }

class StudyReminderForm(forms.ModelForm):
    """Biểu mẫu nhắc nhở học tập"""
    days_of_week_choices = [
        (0, 'Thứ Hai'),
        (1, 'Thứ Ba'),
        (2, 'Thứ Tư'),
        (3, 'Thứ Năm'),
        (4, 'Thứ Sáu'),
        (5, 'Thứ Bảy'),
        (6, 'Chủ Nhật'),
    ]
    
    days_of_week_multiple = forms.MultipleChoiceField(
        choices=days_of_week_choices,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label='Các ngày trong tuần'
    )
    
    class Meta:
        model = StudyReminder
        fields = ['title', 'message', 'reminder_type', 'notification_method', 'reminder_time']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
            'reminder_time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Nếu đang chỉnh sửa, điền các ngày đã chọn
        if self.instance.pk and self.instance.days_of_week:
            selected_days = [int(day) for day in self.instance.days_of_week.split(',')]
            self.initial['days_of_week_multiple'] = selected_days
    
    def clean(self):
        cleaned_data = super().clean()
        reminder_type = cleaned_data.get('reminder_type')
        days_of_week = cleaned_data.get('days_of_week_multiple')
        
        # Nếu là nhắc nhở hàng tuần, phải chọn ít nhất một ngày
        if reminder_type == 'weekly' and not days_of_week:
            self.add_error('days_of_week_multiple', 'Vui lòng chọn ít nhất một ngày trong tuần.')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Lưu các ngày đã chọn dưới dạng chuỗi
        days_of_week = self.cleaned_data.get('days_of_week_multiple')
        if days_of_week:
            instance.days_of_week = ','.join(str(day) for day in days_of_week)
        
        if commit:
            instance.save()
        
        return instance

class UserStrengthWeaknessForm(forms.ModelForm):
    """Biểu mẫu đánh giá điểm mạnh/yếu"""
    class Meta:
        model = UserStrengthWeakness
        fields = ['subject', 'topic', 'is_strength', 'proficiency_score', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'proficiency_score': forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '1'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cập nhật danh sách chủ đề khi chọn môn học
        if self.instance.pk and self.instance.subject:
            self.fields['topic'].queryset = Topic.objects.filter(subject=self.instance.subject)
        else:
            self.fields['topic'].queryset = Topic.objects.none()
        
        # Thêm JavaScript để cập nhật danh sách chủ đề khi thay đổi môn học
        self.fields['subject'].widget.attrs.update({
            'class': 'subject-select',
            'data-topics-url': '/personalization/api/get_topics_by_subject/',
        })
