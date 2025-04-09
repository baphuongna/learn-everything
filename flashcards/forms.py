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


class TextToFlashcardsForm(forms.Form):
    """Form tạo flashcards từ văn bản."""

    text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Nhập văn bản để tạo flashcard tự động...'}),
        label=_('Văn bản'),
        help_text=_('Nhập văn bản để trích xuất các thuật ngữ và định nghĩa')
    )

    flashcard_set = forms.ModelChoiceField(
        queryset=FlashcardSet.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Bộ flashcard'),
        help_text=_('Chọn bộ flashcard để thêm các flashcard mới')
    )

    language = forms.ChoiceField(
        choices=[
            ('en', _('Tiếng Anh')),
            ('vi', _('Tiếng Việt')),
        ],
        initial='vi',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Ngôn ngữ'),
        help_text=_('Ngôn ngữ của văn bản')
    )

    max_cards = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
        label=_('Số lượng flashcard tối đa'),
        help_text=_('Số lượng flashcard tối đa sẽ được tạo')
    )

    use_ai = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_('Sử dụng AI'),
        help_text=_('Sử dụng AI để tạo flashcard chất lượng cao hơn (yêu cầu OpenAI API key)')
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['flashcard_set'].queryset = FlashcardSet.objects.filter(user=user)
