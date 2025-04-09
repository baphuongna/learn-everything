from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from content.models import Subject

# Mục tiêu học tập
class LearningGoal(models.Model):
    """Mục tiêu học tập của người dùng"""
    GOAL_TYPES = [
        ('daily', 'Hàng ngày'),
        ('weekly', 'Hàng tuần'),
        ('monthly', 'Hàng tháng'),
        ('custom', 'Tùy chỉnh'),
    ]

    GOAL_METRICS = [
        ('study_time', 'Thời gian học tập (phút)'),
        ('notes_count', 'Số ghi chú'),
        ('mindmaps_count', 'Số mind map'),
        ('projects_progress', 'Tiến độ dự án (%)'),
        ('exercises_completed', 'Số bài tập hoàn thành'),
        ('competition_points', 'Điểm thi đấu'),
        ('custom', 'Tùy chỉnh'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advanced_learning_goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES, default='daily')
    goal_metric = models.CharField(max_length=20, choices=GOAL_METRICS, default='study_time')
    target_value = models.PositiveIntegerField(help_text='Giá trị mục tiêu')
    current_value = models.PositiveIntegerField(default=0, help_text='Giá trị hiện tại')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='advanced_learning_goals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def get_progress_percentage(self):
        """Tính phần trăm hoàn thành"""
        if self.target_value == 0:
            return 0
        return min(100, int((self.current_value / self.target_value) * 100))

    def update_progress(self, value=None):
        """Cập nhật tiến độ"""
        if value is not None:
            self.current_value = value

        # Kiểm tra xem đã hoàn thành chưa
        if self.current_value >= self.target_value:
            self.is_completed = True

        self.save(update_fields=['current_value', 'is_completed', 'updated_at'])

# Theo dõi thời gian học tập hàng ngày
class DailyStudyLog(models.Model):
    """Theo dõi thời gian học tập hàng ngày"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_logs')
    date = models.DateField(default=timezone.now)
    total_minutes = models.PositiveIntegerField(default=0, help_text='Tổng số phút học tập')
    pomodoro_count = models.PositiveIntegerField(default=0, help_text='Số pomodoro hoàn thành')
    notes_created = models.PositiveIntegerField(default=0, help_text='Số ghi chú đã tạo')
    exercises_completed = models.PositiveIntegerField(default=0, help_text='Số bài tập đã hoàn thành')
    competitions_participated = models.PositiveIntegerField(default=0, help_text='Số cuộc thi đã tham gia')
    competition_points = models.PositiveIntegerField(default=0, help_text='Điểm thi đấu đã kiếm được')
    subjects_studied = models.JSONField(default=dict, help_text='Các môn học đã học và thời gian tương ứng')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    @classmethod
    def get_or_create_today(cls, user):
        """Lấy hoặc tạo bản ghi cho ngày hôm nay"""
        today = timezone.now().date()
        log, created = cls.objects.get_or_create(user=user, date=today)
        return log

    def add_study_time(self, minutes, subject=None):
        """Thêm thời gian học tập"""
        self.total_minutes += minutes

        # Cập nhật thời gian cho môn học
        if subject:
            subjects_dict = self.subjects_studied or {}
            subject_id = str(subject.id)
            subjects_dict[subject_id] = subjects_dict.get(subject_id, 0) + minutes
            self.subjects_studied = subjects_dict

        self.save(update_fields=['total_minutes', 'subjects_studied', 'updated_at'])

        # Cập nhật mục tiêu học tập liên quan
        self.update_related_goals('study_time', minutes, subject)

    def add_pomodoro(self, count=1, subject=None):
        """Thêm số pomodoro hoàn thành"""
        self.pomodoro_count += count
        self.save(update_fields=['pomodoro_count', 'updated_at'])

    def add_note(self, count=1, subject=None):
        """Thêm số ghi chú đã tạo"""
        self.notes_created += count
        self.save(update_fields=['notes_created', 'updated_at'])

        # Cập nhật mục tiêu học tập liên quan
        self.update_related_goals('notes_count', count, subject)

    def add_exercise(self, count=1, subject=None):
        """Thêm số bài tập đã hoàn thành"""
        self.exercises_completed += count
        self.save(update_fields=['exercises_completed', 'updated_at'])

        # Cập nhật mục tiêu học tập liên quan
        self.update_related_goals('exercises_completed', count, subject)

    def add_competition(self, count=1, points=0, subject=None):
        """Thêm số cuộc thi đã tham gia và điểm"""
        self.competitions_participated += count
        self.competition_points += points
        self.save(update_fields=['competitions_participated', 'competition_points', 'updated_at'])

        # Cập nhật mục tiêu học tập liên quan
        self.update_related_goals('competition_points', points, subject)

    def update_related_goals(self, metric_type, value, subject=None):
        """Cập nhật các mục tiêu học tập liên quan"""
        today = timezone.now().date()

        # Lọc các mục tiêu phù hợp
        goals_query = LearningGoal.objects.filter(
            user=self.user,
            goal_metric=metric_type,
            is_active=True,
            is_completed=False,
            start_date__lte=today
        )

        # Lọc theo ngày kết thúc
        goals_query = goals_query.filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
        )

        # Lọc theo môn học nếu có
        if subject:
            goals_query = goals_query.filter(
                models.Q(subject__isnull=True) | models.Q(subject=subject)
            )

        # Cập nhật từng mục tiêu
        for goal in goals_query:
            goal.current_value += value
            goal.update_progress()
