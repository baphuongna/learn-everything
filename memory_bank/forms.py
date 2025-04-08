from django import forms
from .models import MemoryCategory, MemoryItem, MemoryAttachment
from django_summernote.widgets import SummernoteWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, ButtonHolder, Div

class MemoryCategoryForm(forms.ModelForm):
    """Form cho danh mục ghi nhớ"""
    class Meta:
        model = MemoryCategory
        fields = ['name', 'description', 'subject', 'color', 'icon']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
        }

class MemoryItemForm(forms.ModelForm):
    """Form cho ghi nhớ"""
    class Meta:
        model = MemoryItem
        fields = ['category', 'title', 'content', 'priority', 'is_favorite', 'tags']
        widgets = {
            'content': SummernoteWidget(),
            'tags': forms.TextInput(attrs={'placeholder': 'Nhập các thẻ, phân cách bằng dấu phẩy'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Field('category'),
            Field('title'),
            Field('content', css_class='summernote-editor'),
            Field('priority'),
            Field('is_favorite'),
            Field('tags'),
            ButtonHolder(
                Submit('submit', 'Lưu Ghi Nhớ', css_class='btn btn-primary')
            )
        )

class MemoryAttachmentForm(forms.ModelForm):
    """Form cho tập tin đính kèm"""
    class Meta:
        model = MemoryAttachment
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Giới hạn kích thước file (5MB)
            max_size = 5 * 1024 * 1024  # 5MB
            if file.size > max_size:
                raise forms.ValidationError(f"Kích thước file không được vượt quá 5MB.")

            # Kiểm tra loại file
            import os
            from django.core.exceptions import ValidationError

            # Danh sách các đuôi file cho phép
            valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.txt', '.csv', '.xlsx', '.xls']
            # Danh sách MIME types cho phép
            valid_content_types = [
                'application/pdf', 'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'image/jpeg', 'image/png', 'image/gif', 'text/plain', 'text/csv',
                'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            ]

            # Kiểm tra đuôi file
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError(
                    f"Loại file không được hỗ trợ. Các loại file được phép: {', '.join(valid_extensions)}"
                )

            # Kiểm tra MIME type
            content_type = file.content_type
            if content_type not in valid_content_types:
                raise ValidationError(
                    f"Loại nội dung file không được hỗ trợ. Vui lòng tải lên file PDF, Word, Excel, hình ảnh hoặc văn bản."
                )

            # Lưu tên file và loại file
            import re
            # Làm sạch tên file để tránh các ký tự đặc biệt
            clean_name = re.sub(r'[^\w\s.-]', '', file.name)
            self.instance.file_name = clean_name
            self.instance.file_type = content_type
        return file

class MemorySearchForm(forms.Form):
    """Form tìm kiếm ghi nhớ"""
    query = forms.CharField(
        required=False,
        label='Tìm kiếm',
        widget=forms.TextInput(attrs={'placeholder': 'Tìm kiếm ghi nhớ...', 'class': 'form-control'})
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=MemoryCategory.objects.none(),
        label='Danh mục',
        empty_label='Tất cả danh mục',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priority = forms.ChoiceField(
        required=False,
        choices=[('', 'Tất cả mức độ ưu tiên')] + list(MemoryItem.PRIORITY_CHOICES),
        label='Mức độ ưu tiên',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_favorite = forms.BooleanField(
        required=False,
        label='Chỉ hiển thị yêu thích',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = MemoryCategory.objects.filter(user=user)
