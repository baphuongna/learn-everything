from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from content.models import Subject, Topic, Lesson

# Hệ thống học tập dựa trên dự án
class Project(models.Model):
    """Dự án học tập thực tế"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='projects')
    difficulty_level = models.IntegerField(choices=[(1, 'Dễ'), (2, 'Trung bình'), (3, 'Khó')], default=1)
    estimated_hours = models.PositiveIntegerField(help_text='Thời gian ước tính để hoàn thành (giờ)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ProjectTask(models.Model):
    """Nhiệm vụ trong dự án"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.project.title} - {self.title}"

class UserProject(models.Model):
    """Dự án của người dùng"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_projects')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='user_projects')
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Chưa bắt đầu'),
        ('in_progress', 'Đang thực hiện'),
        ('completed', 'Đã hoàn thành')
    ], default='not_started')
    progress = models.PositiveIntegerField(default=0, help_text='Tiến độ hoàn thành (%)')
    notes = models.TextField(blank=True, null=True, help_text='Ghi chú của người dùng về dự án')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.project.title}"

# Bài tập thực hành tương tác
class InteractiveExercise(models.Model):
    """Bài tập thực hành tương tác"""
    EXERCISE_TYPES = [
        ('code', 'Bài tập lập trình'),
        ('quiz', 'Câu đố tương tác'),
        ('simulation', 'Mô phỏng'),
        ('game', 'Trò chơi học tập')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='interactive_exercises')
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    content = models.TextField(help_text='Nội dung bài tập (có thể là mã HTML, JavaScript, hoặc mã nguồn)')
    solution = models.TextField(help_text='Giải pháp hoặc đáp án', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Hệ thống ghi chú Cornell
class CornellNote(models.Model):
    """Ghi chú theo phương pháp Cornell"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cornell_notes')
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='cornell_notes')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='cornell_notes')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='cornell_notes')
    main_notes = models.TextField(help_text='Phần ghi chú chính')
    cue_column = models.TextField(help_text='Phần cột gợi ý (câu hỏi, từ khóa)', blank=True)
    summary = models.TextField(help_text='Phần tóm tắt', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Phương pháp Feynman Technique
class FeynmanNote(models.Model):
    """Ghi chú theo phương pháp Feynman"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feynman_notes')
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='feynman_notes')
    concept = models.TextField(help_text='Khái niệm cần giải thích')
    explanation = models.TextField(help_text='Giải thích bằng ngôn ngữ đơn giản')
    gaps_identified = models.TextField(help_text='Các lỗ hổng kiến thức đã xác định', blank=True)
    refined_explanation = models.TextField(help_text='Giải thích đã được cải thiện', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Hệ thống Mind Mapping
class MindMap(models.Model):
    """Sơ đồ tư duy"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mind_maps')
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='mind_maps')
    central_topic = models.CharField(max_length=200, help_text='Chủ đề trung tâm')
    map_data = models.JSONField(help_text='Dữ liệu sơ đồ tư duy dạng JSON')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Pomodoro Timer
class PomodoroSession(models.Model):
    """Phiên học tập Pomodoro"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pomodoro_sessions')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='pomodoro_sessions')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='pomodoro_sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    work_duration = models.PositiveIntegerField(default=25, help_text='Thời gian làm việc (phút)')
    break_duration = models.PositiveIntegerField(default=5, help_text='Thời gian nghỉ (phút)')
    completed_pomodoros = models.PositiveIntegerField(default=0, help_text='Số pomodoro đã hoàn thành')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

# Chế độ thi đấu
class CompetitionMode(models.Model):
    """Chế độ thi đấu"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='competitions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    time_limit = models.PositiveIntegerField(help_text='Thời gian làm bài (phút)')
    max_participants = models.PositiveIntegerField(default=0, help_text='Số người tham gia tối đa (0 = không giới hạn)')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class CompetitionQuestion(models.Model):
    """Câu hỏi trong chế độ thi đấu"""
    competition = models.ForeignKey(CompetitionMode, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    points = models.PositiveIntegerField(default=1, help_text='Điểm cho câu hỏi này')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.competition.title} - Câu hỏi {self.order}"

class CompetitionAnswer(models.Model):
    """Đáp án cho câu hỏi trong chế độ thi đấu"""
    question = models.ForeignKey(CompetitionQuestion, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.question} - {self.answer_text[:30]}"

class CompetitionParticipant(models.Model):
    """Người tham gia chế độ thi đấu"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='competition_participations')
    competition = models.ForeignKey(CompetitionMode, on_delete=models.CASCADE, related_name='participants')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.competition.title}"

# Hệ thống thông báo
class Notification(models.Model):
    """Thông báo cho người dùng"""
    NOTIFICATION_TYPES = [
        ('info', 'Thông tin'),
        ('success', 'Thành công'),
        ('warning', 'Cảnh báo'),
        ('danger', 'Quan trọng'),
    ]

    RELATED_FEATURES = [
        ('pomodoro', 'Pomodoro Timer'),
        ('cornell', 'Cornell Notes'),
        ('mindmap', 'Mind Mapping'),
        ('feynman', 'Feynman Technique'),
        ('project', 'Project-Based Learning'),
        ('exercise', 'Interactive Exercises'),
        ('competition', 'Competition Mode'),
        ('system', 'Hệ thống'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advanced_notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    related_feature = models.CharField(max_length=20, choices=RELATED_FEATURES, default='system')
    related_object_id = models.IntegerField(null=True, blank=True)  # ID của đối tượng liên quan (nếu có)
    url = models.CharField(max_length=200, blank=True)  # URL để chuyển hướng khi nhấp vào thông báo
    is_read = models.BooleanField(default=False)  # Đánh dấu đã đọc hay chưa
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"
