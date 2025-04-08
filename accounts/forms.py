from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, ButtonHolder
from .models import UserProfile, StudySession

class CustomUserCreationForm(UserCreationForm):
    """Form đăng ký người dùng tùy chỉnh với crispy-forms"""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Field('username', css_class='form-control', autocomplete='username'),
            Field('email', css_class='form-control', autocomplete='email'),
            Field('password1', css_class='form-control', autocomplete='new-password'),
            Field('password2', css_class='form-control', autocomplete='new-password'),
            ButtonHolder(
                Submit('submit', 'Đăng Ký', css_class='btn btn-primary btn-block mt-4')
            )
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    """Form đăng nhập tùy chỉnh với crispy-forms"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Field('username', css_class='form-control', autocomplete='username'),
            Field('password', css_class='form-control', autocomplete='current-password'),
            ButtonHolder(
                Submit('submit', 'Đăng Nhập', css_class='btn btn-primary btn-block mt-4')
            )
        )

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
