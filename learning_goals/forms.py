from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from .models import LearningGoal, GoalProgress, GoalInvitation, GoalCollaborator

class LearningGoalForm(forms.ModelForm):
    """Form tạo và chỉnh sửa mục tiêu học tập"""

    class Meta:
        model = LearningGoal
        fields = [
            'title', 'description', 'goal_type', 'category',
            'start_date', 'end_date', 'target_value',
            'subject', 'topic', 'lesson',
            'reminder_enabled', 'reminder_frequency', 'reminder_days_before', 'reminder_time',
            'reminder_email', 'reminder_app',
            'reward_points', 'has_badge_reward', 'badge_name', 'badge_description', 'badge_level',
            'is_public', 'allow_collaboration',
            'is_recurring', 'recurring_frequency'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'reminder_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Thêm class Bootstrap cho các trường
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        # Thêm placeholder
        self.fields['title'].widget.attrs['placeholder'] = 'Nhập tiêu đề mục tiêu'
        self.fields['description'].widget.attrs['placeholder'] = 'Mô tả chi tiết về mục tiêu của bạn'
        self.fields['target_value'].widget.attrs['placeholder'] = 'Nhập giá trị mục tiêu (ví dụ: số phút, số bài học, ...)'

        # Các trường không bắt buộc
        self.fields['subject'].required = False
        self.fields['topic'].required = False
        self.fields['lesson'].required = False
        self.fields['description'].required = False
        self.fields['badge_name'].required = False
        self.fields['badge_description'].required = False

        # Thêm placeholder cho các trường phần thưởng
        self.fields['reward_points'].widget.attrs['placeholder'] = 'Số điểm thưởng khi hoàn thành mục tiêu'
        self.fields['badge_name'].widget.attrs['placeholder'] = 'Tên huy hiệu thưởng (nếu có)'
        self.fields['badge_description'].widget.attrs['placeholder'] = 'Mô tả huy hiệu thưởng'

        # Thêm widget cho badge_description
        self.fields['badge_description'].widget = forms.Textarea(attrs={'rows': 2, 'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        goal_type = cleaned_data.get('goal_type')

        # Kiểm tra ngày bắt đầu và kết thúc
        if start_date and end_date:
            if start_date > end_date:
                self.add_error('end_date', 'Ngày kết thúc phải sau ngày bắt đầu')

            # Kiểm tra thời gian phù hợp với loại mục tiêu
            duration = (end_date - start_date).days + 1

            if goal_type == 'daily' and duration != 1:
                self.add_error('goal_type', 'Mục tiêu hàng ngày phải có thời gian là 1 ngày')
            elif goal_type == 'weekly' and (duration < 5 or duration > 8):
                self.add_error('goal_type', 'Mục tiêu hàng tuần nên có thời gian từ 5-8 ngày')
            elif goal_type == 'monthly' and (duration < 25 or duration > 35):
                self.add_error('goal_type', 'Mục tiêu hàng tháng nên có thời gian từ 25-35 ngày')

        return cleaned_data

class GoalProgressForm(forms.Form):
    """Form cập nhật tiến độ mục tiêu"""
    value = forms.IntegerField(
        min_value=0,
        label='Giá trị hiện tại',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập giá trị hiện tại'
        })
    )
    notes = forms.CharField(
        required=False,
        label='Ghi chú',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Ghi chú về tiến độ (không bắt buộc)',
            'rows': 3
        })
    )

class GoalInvitationForm(forms.Form):
    """Form mời người dùng tham gia mục tiêu"""
    username = forms.CharField(
        label='Tên người dùng',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên người dùng'
        })
    )
    role = forms.ChoiceField(
        label='Vai trò',
        choices=GoalCollaborator.ROLE_CHOICES,
        initial='viewer',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    message = forms.CharField(
        required=False,
        label='Lời nhắn',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Lời nhắn gửi kèm lời mời (không bắt buộc)',
            'rows': 3
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            user = User.objects.get(username=username)
            return username
        except User.DoesNotExist:
            raise forms.ValidationError('Người dùng không tồn tại')

class GoalCommentForm(forms.Form):
    """Form bình luận về mục tiêu"""
    content = forms.CharField(
        label='Bình luận',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập bình luận của bạn',
            'rows': 3
        })
    )

class ReminderSettingsForm(forms.Form):
    """Form cài đặt nhắc nhở cho tất cả các mục tiêu"""
    reminder_enabled = forms.BooleanField(
        label='Bật nhắc nhở cho tất cả mục tiêu',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    reminder_frequency = forms.ChoiceField(
        label='Tần suất nhắc nhở',
        choices=[('daily', 'Hàng ngày'), ('weekly', 'Hàng tuần')],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    reminder_days_before = forms.IntegerField(
        label='Số ngày nhắc trước hạn',
        min_value=0,
        max_value=30,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    reminder_time = forms.TimeField(
        label='Thời gian nhắc nhở',
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    reminder_email = forms.BooleanField(
        label='Gửi nhắc nhở qua email',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    reminder_app = forms.BooleanField(
        label='Gửi nhắc nhở trong ứng dụng',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    apply_to_all = forms.BooleanField(
        label='Áp dụng cho tất cả mục tiêu hiện tại',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
