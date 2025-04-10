from django.db import models
from django.contrib.auth.models import User
from content.models import Subject, Topic, Lesson
from quizzes.models import Quiz, QuizAttempt
from flashcards.models import FlashcardSet, SpacedRepetitionSchedule
from accounts.models import StudySession

class AnalyticsPreference(models.Model):
    """Lưu trữ các tùy chọn phân tích dữ liệu của người dùng"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='analytics_preferences')
    show_study_time = models.BooleanField(default=True, help_text='Hiển thị thời gian học tập')
    show_quiz_performance = models.BooleanField(default=True, help_text='Hiển thị hiệu suất làm bài kiểm tra')
    show_flashcard_performance = models.BooleanField(default=True, help_text='Hiển thị hiệu suất học flashcard')
    show_subject_distribution = models.BooleanField(default=True, help_text='Hiển thị phân bố thời gian theo chủ đề')
    show_learning_patterns = models.BooleanField(default=True, help_text='Hiển thị mẫu học tập')
    show_recommendations = models.BooleanField(default=True, help_text='Hiển thị đề xuất học tập')
    dashboard_refresh_rate = models.IntegerField(default=24, help_text='Tần suất làm mới bảng điều khiển (giờ)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tùy chọn phân tích của {self.user.username}"

class LearningMetric(models.Model):
    """Lưu trữ các chỉ số học tập của người dùng"""
    METRIC_TYPES = [
        ('study_time', 'Thời gian học tập'),
        ('quiz_score', 'Điểm bài kiểm tra'),
        ('flashcard_retention', 'Tỷ lệ ghi nhớ flashcard'),
        ('completion_rate', 'Tỷ lệ hoàn thành'),
        ('focus_score', 'Điểm tập trung'),
        ('consistency_score', 'Điểm độ đều'),
        ('custom', 'Tùy chỉnh')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_metrics')
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='metrics')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='metrics')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='metrics')
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'metric_type']

    def __str__(self):
        return f"{self.metric_name}: {self.metric_value} ({self.date})"

class AnalyticsReport(models.Model):
    """Lưu trữ các báo cáo phân tích"""
    REPORT_TYPES = [
        ('daily', 'Hàng ngày'),
        ('weekly', 'Hàng tuần'),
        ('monthly', 'Hàng tháng'),
        ('custom', 'Tùy chỉnh')
    ]

    REPORT_FORMATS = [
        ('html', 'HTML'),
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('json', 'JSON')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_reports')
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    report_format = models.CharField(max_length=10, choices=REPORT_FORMATS, default='html')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    report_data = models.JSONField(default=dict)
    is_generated = models.BooleanField(default=False)
    file_path = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"

class LearningRecommendation(models.Model):
    """Lưu trữ các đề xuất học tập"""
    RECOMMENDATION_TYPES = [
        ('subject', 'Chủ đề'),
        ('topic', 'Chủ đề con'),
        ('lesson', 'Bài học'),
        ('quiz', 'Bài kiểm tra'),
        ('flashcard', 'Flashcard'),
        ('study_habit', 'Thói quen học tập'),
        ('custom', 'Tùy chỉnh')
    ]

    PRIORITY_LEVELS = [
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_recommendations')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_recommendations')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_recommendations')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_recommendations')
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, blank=True, related_name='recommendations')
    flashcard_set = models.ForeignKey(FlashcardSet, on_delete=models.SET_NULL, null=True, blank=True, related_name='recommendations')
    is_dismissed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_recommendation_type_display()})"

class LearningInsight(models.Model):
    """Lưu trữ các phân tích sâu về học tập"""
    INSIGHT_TYPES = [
        ('strength', 'Điểm mạnh'),
        ('weakness', 'Điểm yếu'),
        ('pattern', 'Mẫu học tập'),
        ('improvement', 'Cải thiện'),
        ('milestone', 'Cột mốc'),
        ('custom', 'Tùy chỉnh')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_insights')
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    data_points = models.JSONField(default=dict, help_text='Dữ liệu hỗ trợ cho phân tích')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_insights')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_insights')
    is_highlighted = models.BooleanField(default=False, help_text='Nổi bật trên bảng điều khiển')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_insight_type_display()})"