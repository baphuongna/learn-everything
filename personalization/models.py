from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from content.models import Subject, Topic, Lesson
from accounts.models import UserProfile

class LearningPathway(models.Model):
    """Lộ trình học tập cá nhân hóa"""
    DIFFICULTY_LEVELS = [
        ('beginner', 'Người mới bắt đầu'),
        ('intermediate', 'Trung cấp'),
        ('advanced', 'Nâng cao'),
        ('expert', 'Chuyên gia'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_pathways')
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='learning_pathways')
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='beginner')
    estimated_duration_days = models.PositiveIntegerField(default=30, help_text='Thời gian ước tính để hoàn thành (ngày)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def get_progress_percentage(self):
        """Tính phần trăm hoàn thành của lộ trình"""
        total_steps = self.pathway_steps.count()
        if total_steps == 0:
            return 0
        completed_steps = self.pathway_steps.filter(is_completed=True).count()
        return int((completed_steps / total_steps) * 100)

class PathwayStep(models.Model):
    """Bước trong lộ trình học tập"""
    STEP_TYPES = [
        ('lesson', 'Bài học'),
        ('quiz', 'Bài kiểm tra'),
        ('exercise', 'Bài tập thực hành'),
        ('project', 'Dự án nhỏ'),
        ('assessment', 'Đánh giá'),
    ]

    pathway = models.ForeignKey(LearningPathway, on_delete=models.CASCADE, related_name='pathway_steps')
    title = models.CharField(max_length=200)
    description = models.TextField()
    step_type = models.CharField(max_length=20, choices=STEP_TYPES)
    order = models.PositiveIntegerField(default=0, help_text='Thứ tự của bước trong lộ trình')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='pathway_steps')
    external_content_url = models.URLField(blank=True, null=True, help_text='URL đến nội dung bên ngoài nếu có')
    estimated_duration_minutes = models.PositiveIntegerField(default=30, help_text='Thời gian ước tính để hoàn thành (phút)')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['pathway', 'order']

    def __str__(self):
        return f"{self.pathway.title} - {self.title}"

    def mark_as_completed(self):
        """Đánh dấu bước đã hoàn thành"""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()

        # Kiểm tra xem tất cả các bước đã hoàn thành chưa
        pathway = self.pathway
        all_steps = pathway.pathway_steps.count()
        completed_steps = pathway.pathway_steps.filter(is_completed=True).count()

        # Nếu đã hoàn thành tất cả các bước, tạo thông báo
        if all_steps == completed_steps:
            from notifications.models import Notification
            Notification.objects.create(
                user=pathway.user,
                title=f"Chúc mừng! Bạn đã hoàn thành lộ trình {pathway.title}",
                message=f"Bạn đã hoàn thành tất cả {all_steps} bước trong lộ trình học tập {pathway.title}.",
                notification_type='success',
                related_feature='personalization'
            )

class LearningPreference(models.Model):
    """Sở thích học tập của người dùng"""
    LEARNING_STYLES = [
        ('visual', 'Học bằng hình ảnh'),
        ('auditory', 'Học bằng âm thanh'),
        ('reading', 'Học bằng đọc'),
        ('kinesthetic', 'Học bằng thực hành'),
    ]

    DIFFICULTY_PREFERENCES = [
        ('easy_to_hard', 'Từ dễ đến khó'),
        ('hard_to_easy', 'Từ khó đến dễ'),
        ('mixed', 'Kết hợp'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learning_preference')
    preferred_learning_style = models.CharField(max_length=20, choices=LEARNING_STYLES, default='visual')
    preferred_difficulty = models.CharField(max_length=20, choices=DIFFICULTY_PREFERENCES, default='easy_to_hard')
    preferred_study_time = models.TimeField(default=timezone.now, help_text='Thời gian học tập ưa thích')
    preferred_session_duration = models.PositiveIntegerField(default=30, help_text='Thời lượng phiên học ưa thích (phút)')
    preferred_topics = models.ManyToManyField(Topic, blank=True, related_name='interested_users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sở thích học tập của {self.user.username}"

class ContentRecommendation(models.Model):
    """Đề xuất nội dung học tập cho người dùng"""
    RECOMMENDATION_TYPES = [
        ('lesson', 'Bài học'),
        ('quiz', 'Bài kiểm tra'),
        ('flashcard', 'Flashcard'),
        ('exercise', 'Bài tập thực hành'),
        ('project', 'Dự án học tập'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_recommendations')
    title = models.CharField(max_length=200)
    description = models.TextField()
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='recommendations')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='recommendations')
    external_content_url = models.URLField(blank=True, null=True)
    relevance_score = models.FloatField(default=0.0, help_text='Điểm liên quan từ 0.0 đến 1.0')
    is_viewed = models.BooleanField(default=False)
    is_helpful = models.BooleanField(null=True, blank=True, help_text='Người dùng đánh giá đề xuất có hữu ích không')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-relevance_score', '-created_at']

    def __str__(self):
        return f"Đề xuất: {self.title} cho {self.user.username}"

class UserInteraction(models.Model):
    """Lưu trữ tương tác của người dùng với nội dung"""
    INTERACTION_TYPES = [
        ('view', 'Xem'),
        ('complete', 'Hoàn thành'),
        ('like', 'Thích'),
        ('bookmark', 'Đánh dấu'),
        ('share', 'Chia sẻ'),
        ('rate', 'Đánh giá'),
    ]

    CONTENT_TYPES = [
        ('lesson', 'Bài học'),
        ('quiz', 'Bài kiểm tra'),
        ('flashcard', 'Flashcard'),
        ('exercise', 'Bài tập thực hành'),
        ('project', 'Dự án học tập'),
        ('pathway', 'Lộ trình học tập'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_id = models.PositiveIntegerField(help_text='ID của nội dung tương tác')
    rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Đánh giá từ 1-5 sao')
    interaction_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-interaction_time']
        indexes = [
            models.Index(fields=['user', 'content_type', 'content_id']),
            models.Index(fields=['content_type', 'content_id']),
        ]

    def __str__(self):
        return f"{self.user.username} {self.get_interaction_type_display()} {self.content_type} {self.content_id}"

class UserStrengthWeakness(models.Model):
    """Lưu trữ điểm mạnh và điểm yếu của người dùng"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='strengths_weaknesses')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='user_assessments')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_assessments')
    is_strength = models.BooleanField(default=True, help_text='True nếu là điểm mạnh, False nếu là điểm yếu')
    proficiency_score = models.FloatField(default=0.0, help_text='Điểm thành thạo từ 0.0 đến 1.0')
    last_assessment_date = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, help_text='Ghi chú về điểm mạnh/yếu')

    class Meta:
        ordering = ['-proficiency_score']
        unique_together = ['user', 'subject', 'topic']

    def __str__(self):
        strength_or_weakness = "Điểm mạnh" if self.is_strength else "Điểm yếu"
        topic_name = f" - {self.topic.name}" if self.topic else ""
        return f"{strength_or_weakness} của {self.user.username}: {self.subject.name}{topic_name}"

class UIPreference(models.Model):
    """Tùy chỉnh giao diện người dùng"""
    COLOR_THEMES = [
        ('light', 'Sáng'),
        ('dark', 'Tối'),
        ('blue', 'Xanh dương'),
        ('green', 'Xanh lá'),
        ('purple', 'Tím'),
        ('orange', 'Cam'),
    ]

    FONT_SIZES = [
        ('small', 'Nhỏ'),
        ('medium', 'Vừa'),
        ('large', 'Lớn'),
        ('x-large', 'Rất lớn'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ui_preference')
    color_theme = models.CharField(max_length=20, choices=COLOR_THEMES, default='light')
    font_size = models.CharField(max_length=20, choices=FONT_SIZES, default='medium')
    enable_animations = models.BooleanField(default=True)
    sidebar_collapsed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tùy chỉnh giao diện của {self.user.username}"

class StudyReminder(models.Model):
    """Nhắc nhở học tập cá nhân hóa"""
    REMINDER_TYPES = [
        ('daily', 'Hàng ngày'),
        ('weekly', 'Hàng tuần'),
        ('custom', 'Tùy chỉnh'),
    ]

    NOTIFICATION_METHODS = [
        ('app', 'Thông báo trong ứng dụng'),
        ('email', 'Email'),
        ('both', 'Cả hai'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_reminders')
    title = models.CharField(max_length=200)
    message = models.TextField()
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES, default='daily')
    notification_method = models.CharField(max_length=20, choices=NOTIFICATION_METHODS, default='app')
    reminder_time = models.TimeField(default=timezone.now)
    days_of_week = models.CharField(max_length=20, blank=True, help_text='Các ngày trong tuần, định dạng: 0,1,2,3,4,5,6 (0=Thứ Hai)')
    is_active = models.BooleanField(default=True)
    last_sent = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Nhắc nhở: {self.title} cho {self.user.username}"

    def should_send_today(self):
        """Kiểm tra xem hôm nay có cần gửi nhắc nhở không"""
        today = timezone.now().date()

        # Nếu đã gửi hôm nay rồi thì không gửi nữa
        if self.last_sent and self.last_sent.date() == today:
            return False

        # Nhắc nhở hàng ngày
        if self.reminder_type == 'daily':
            return True

        # Nhắc nhở hàng tuần
        if self.reminder_type == 'weekly' and self.days_of_week:
            weekday = today.weekday()  # 0=Thứ Hai, 6=Chủ Nhật
            return str(weekday) in self.days_of_week.split(',')

        return False
