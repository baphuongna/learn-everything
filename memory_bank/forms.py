from django import forms
from .models import MemoryCategory, MemoryItem, MemoryAttachment
from django_summernote.widgets import SummernoteWidget

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

class MemoryAttachmentForm(forms.ModelForm):
    """Form cho tập tin đính kèm"""
    class Meta:
        model = MemoryAttachment
        fields = ['file']
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Giới hạn kích thước file (10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Kích thước file không được vượt quá 10MB.")
            
            # Lưu tên file và loại file
            self.instance.file_name = file.name
            self.instance.file_type = file.content_type
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
