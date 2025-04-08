from django import forms
from .models import CornellNote, FeynmanNote, MindMap, Project, ProjectTask, UserProject, InteractiveExercise, CompetitionMode, CompetitionQuestion, CompetitionAnswer, CompetitionParticipant
from content.models import Topic, Lesson, Subject

class CornellNoteForm(forms.ModelForm):
    """Form cho ghi chú Cornell"""
    class Meta:
        model = CornellNote
        fields = ['title', 'subject', 'topic', 'lesson', 'main_notes', 'cue_column', 'summary']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tiêu đề ghi chú'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'topic': forms.Select(attrs={'class': 'form-select'}),
            'lesson': forms.Select(attrs={'class': 'form-select'}),
            'main_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Nội dung ghi chú chính'
            }),
            'cue_column': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Câu hỏi, từ khóa, gợi ý'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Tóm tắt nội dung chính'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thiết lập các trường không bắt buộc
        self.fields['topic'].required = False
        self.fields['lesson'].required = False
        self.fields['cue_column'].required = False
        self.fields['summary'].required = False

        # Lọc các topic dựa trên subject được chọn
        if 'subject' in self.data:
            try:
                subject_id = int(self.data.get('subject'))
                self.fields['topic'].queryset = Topic.objects.filter(subject_id=subject_id).order_by('order')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.subject:
            self.fields['topic'].queryset = Topic.objects.filter(subject=self.instance.subject).order_by('order')
        else:
            self.fields['topic'].queryset = Topic.objects.none()

        # Lọc các lesson dựa trên topic được chọn
        if 'topic' in self.data:
            try:
                topic_id = int(self.data.get('topic'))
                self.fields['lesson'].queryset = Lesson.objects.filter(topic_id=topic_id).order_by('order')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.topic:
            self.fields['lesson'].queryset = Lesson.objects.filter(topic=self.instance.topic).order_by('order')
        else:
            self.fields['lesson'].queryset = Lesson.objects.none()

class MindMapForm(forms.ModelForm):
    """Form cho sơ đồ tư duy"""
    class Meta:
        model = MindMap
        fields = ['title', 'subject', 'central_topic', 'map_data']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tiêu đề sơ đồ tư duy'
            }),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'central_topic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Chủ đề trung tâm của sơ đồ'
            }),
            'map_data': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thiết lập các trường không bắt buộc
        self.fields['subject'].required = False

        # Khởi tạo giá trị mặc định cho map_data nếu là form tạo mới
        if not self.instance.pk and not self.data.get('map_data'):
            # Cấu trúc dữ liệu mặc định cho sơ đồ tư duy mới
            default_map_data = {
                'id': 'root',
                'type': 'root',
                'text': 'Chủ đề trung tâm',
                'children': []
            }
            self.initial['map_data'] = default_map_data

class FeynmanNoteForm(forms.ModelForm):
    """Form cho ghi chú theo phương pháp Feynman"""
    class Meta:
        model = FeynmanNote
        fields = ['title', 'subject', 'concept', 'explanation', 'gaps_identified', 'refined_explanation']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tiêu đề ghi chú'
            }),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'concept': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Nhập khái niệm hoặc chủ đề bạn muốn hiểu sâu sắc'
            }),
            'explanation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Giải thích khái niệm bằng ngôn ngữ đơn giản như thể bạn đang dạy cho một đứa trẻ 12 tuổi'
            }),
            'gaps_identified': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Xác định những lỗ hổng trong hiểu biết của bạn hoặc những phần bạn còn chưa giải thích được rõ ràng'
            }),
            'refined_explanation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Giải thích lại khái niệm sau khi đã điền vào các lỗ hổng kiến thức và cải thiện sự hiểu biết của bạn'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thiết lập các trường không bắt buộc
        self.fields['subject'].required = False
        self.fields['gaps_identified'].required = False
        self.fields['refined_explanation'].required = False

class ProjectForm(forms.ModelForm):
    """Form cho dự án học tập"""
    class Meta:
        model = Project
        fields = ['title', 'description', 'subject', 'difficulty_level', 'estimated_hours']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tiêu đề dự án'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Mô tả chi tiết về dự án'
            }),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'difficulty_level': forms.Select(attrs={'class': 'form-select'}),
            'estimated_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Thời gian ước tính để hoàn thành (giờ)'
            }),
        }

class ProjectTaskForm(forms.ModelForm):
    """Form cho nhiệm vụ trong dự án"""
    class Meta:
        model = ProjectTask
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tiêu đề nhiệm vụ'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Mô tả chi tiết về nhiệm vụ'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Thứ tự nhiệm vụ'
            }),
        }

class UserProjectForm(forms.ModelForm):
    """Form cho dự án của người dùng"""
    class Meta:
        model = UserProject
        fields = ['status', 'progress', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'progress': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'placeholder': 'Tiến độ hoàn thành (%)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ghi chú của bạn về dự án'
            }),
        }

class InteractiveExerciseForm(forms.ModelForm):
    """Form cho bài tập thực hành tương tác"""
    class Meta:
        model = InteractiveExercise
        fields = ['title', 'description', 'lesson', 'exercise_type', 'content', 'solution']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tiêu đề bài tập'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Mô tả bài tập'
            }),
            'lesson': forms.Select(attrs={'class': 'form-select'}),
            'exercise_type': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Nội dung bài tập (HTML, JavaScript, hoặc mã nguồn)'
            }),
            'solution': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Giải pháp hoặc đáp án cho bài tập'
            }),
        }

class CompetitionForm(forms.ModelForm):
    """Form cho chế độ thi đấu"""
    class Meta:
        model = CompetitionMode
        fields = ['title', 'description', 'subject', 'start_time', 'end_time', 'time_limit', 'max_participants', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tiêu đề cuộc thi'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Mô tả cuộc thi'
            }),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'time_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Thời gian làm bài (phút)'
            }),
            'max_participants': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Số người tham gia tối đa (0 = không giới hạn)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class CompetitionQuestionForm(forms.ModelForm):
    """Form cho câu hỏi trong chế độ thi đấu"""
    class Meta:
        model = CompetitionQuestion
        fields = ['question_text', 'points', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Nội dung câu hỏi'
            }),
            'points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Điểm cho câu hỏi này'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Thứ tự câu hỏi'
            }),
        }

class CompetitionAnswerForm(forms.ModelForm):
    """Form cho đáp án trong chế độ thi đấu"""
    class Meta:
        model = CompetitionAnswer
        fields = ['answer_text', 'is_correct']
        widgets = {
            'answer_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Nội dung đáp án'
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class CompetitionParticipantForm(forms.ModelForm):
    """Form cho người tham gia chế độ thi đấu"""
    class Meta:
        model = CompetitionParticipant
        fields = ['competition']
        widgets = {
            'competition': forms.Select(attrs={'class': 'form-select'}),
        }
