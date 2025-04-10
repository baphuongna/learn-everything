"""
Forms cho ứng dụng learning_analytics.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from content.models import Subject, Topic
from .models import AnalyticsPreference, AnalyticsReport

class AnalyticsPreferenceForm(forms.ModelForm):
    """Form tùy chọn phân tích dữ liệu."""

    class Meta:
        model = AnalyticsPreference
        fields = [
            'show_study_time',
            'show_quiz_performance',
            'show_flashcard_performance',
            'show_subject_distribution',
            'show_learning_patterns',
            'show_recommendations',
            'dashboard_refresh_rate'
        ]
        widgets = {
            'show_study_time': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_quiz_performance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_flashcard_performance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_subject_distribution': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_learning_patterns': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_recommendations': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dashboard_refresh_rate': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 72})
        }

class ReportFilterForm(forms.Form):
    """Form lọc báo cáo phân tích."""

    REPORT_TYPES = [
        ('daily', _('Hàng ngày')),
        ('weekly', _('Hàng tuần')),
        ('monthly', _('Hàng tháng')),
        ('custom', _('Tùy chỉnh'))
    ]

    REPORT_FORMATS = [
        ('html', 'HTML'),
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('json', 'JSON')
    ]

    report_type = forms.ChoiceField(
        choices=REPORT_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Loại báo cáo')
    )

    report_format = forms.ChoiceField(
        choices=REPORT_FORMATS,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Định dạng báo cáo'),
        initial='html'
    )

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label=_('Ngày bắt đầu')
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label=_('Ngày kết thúc')
    )

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Chủ đề'),
        required=False
    )

    topic = forms.ModelChoiceField(
        queryset=Topic.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Chủ đề con'),
        required=False
    )

    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('Tiêu đề báo cáo'),
        required=False
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label=_('Mô tả báo cáo'),
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

class ShareReportForm(forms.Form):
    """
    Form chia sẻ báo cáo phân tích qua email.
    """
    recipient_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@example.com'}),
        label=_('Email người nhận')
    )

    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('Tiêu đề email'),
        initial=_('Báo cáo phân tích học tập')
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label=_('Nội dung email'),
        required=False
    )

    attach_file = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_('Đính kèm báo cáo'),
        initial=True,
        required=False
    )
