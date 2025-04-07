from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, StudySession

class UserForm(forms.ModelForm):
    """Form cho thông tin người dùng cơ bản"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UserProfileForm(forms.ModelForm):
    """Form cho thông tin hồ sơ người dùng"""
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'preferred_subjects', 'daily_goal_minutes']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'preferred_subjects': forms.CheckboxSelectMultiple(),
        }

class StudySessionForm(forms.ModelForm):
    """Form ghi lại phiên học tập"""
    class Meta:
        model = StudySession
        fields = ['subject', 'start_time', 'end_time', 'duration_minutes', 'notes']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        """Kiểm tra dữ liệu hợp lệ"""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        duration_minutes = cleaned_data.get('duration_minutes')
        
        if start_time and end_time:
            # Kiểm tra thời gian kết thúc phải sau thời gian bắt đầu
            if end_time <= start_time:
                raise forms.ValidationError("Thời gian kết thúc phải sau thời gian bắt đầu.")
            
            # Tính toán thời gian học tập
            duration = (end_time - start_time).total_seconds() / 60
            
            # Kiểm tra thời gian học tập có phù hợp với thời lượng đã nhập không
            if duration_minutes and abs(duration - duration_minutes) > 5:
                raise forms.ValidationError(
                    f"Thời lượng học tập ({duration_minutes} phút) không khớp với khoảng thời gian "
                    f"({duration:.0f} phút). Vui lòng kiểm tra lại."
                )
        
        return cleaned_data
