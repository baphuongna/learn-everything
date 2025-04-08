from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from content.models import Subject, Topic, Lesson

class LearningGoal(models.Model):
    """Mục tiêu học tập của người dùng"""

    GOAL_TYPES = [
        ('daily', 'Hàng ngày'),
        ('weekly', 'Hàng tuần'),
        ('monthly', 'Hàng tháng'),
    ]

    GOAL_STATUS = [
        ('not_started', 'Chưa bắt đầu'),
        ('in_progress', 'Đang thực hiện'),
        ('completed', 'Đã hoàn thành'),
        ('overdue', 'Quá hạn'),
    ]

    GOAL_CATEGORIES = [
        ('study_time', 'Thời gian học tập'),
        ('lessons_completed', 'Số bài học hoàn thành'),
        ('flashcards_reviewed', 'Số flashcard ôn tập'),
        ('quizzes_completed', 'Số bài kiểm tra hoàn thành'),
        ('projects_completed', 'Số dự án hoàn thành'),
        ('custom', 'Tùy chỉnh'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_goals')
    title = models.CharField(max_length=200, verbose_name='Tiêu đề')
    description = models.TextField(blank=True, verbose_name='Mô tả')

    # Loại mục tiêu
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES, default='weekly', verbose_name='Loại mục tiêu')
    category = models.CharField(max_length=20, choices=GOAL_CATEGORIES, default='study_time', verbose_name='Danh mục')

    # Thời gian
    start_date = models.DateField(default=timezone.now, verbose_name='Ngày bắt đầu')
    end_date = models.DateField(verbose_name='Ngày kết thúc')

    # Mục tiêu và tiến độ
    target_value = models.PositiveIntegerField(default=1, verbose_name='Giá trị mục tiêu')
    current_value = models.PositiveIntegerField(default=0, verbose_name='Giá trị hiện tại')
    progress_percentage = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Phần trăm tiến độ')

    # Trạng thái
    status = models.CharField(max_length=20, choices=GOAL_STATUS, default='not_started', verbose_name='Trạng thái')

    # Liên kết với nội dung (tùy chọn)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='goals', verbose_name='Chủ đề')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='goals', verbose_name='Chủ đề con')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='goals', verbose_name='Bài học')

    # Thông báo
    reminder_enabled = models.BooleanField(default=True, verbose_name='Bật nhắc nhở')
    reminder_frequency = models.CharField(max_length=20, choices=[('daily', 'Hàng ngày'), ('weekly', 'Hàng tuần')], default='daily', verbose_name='Tần suất nhắc nhở')

    # Phần thưởng
    reward_points = models.PositiveIntegerField(default=10, verbose_name='Điểm thưởng')
    has_badge_reward = models.BooleanField(default=False, verbose_name='Có huy hiệu thưởng')
    badge_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Tên huy hiệu')
    badge_description = models.TextField(blank=True, null=True, verbose_name='Mô tả huy hiệu')
    badge_level = models.CharField(max_length=20, choices=[('bronze', 'Đồng'), ('silver', 'Bạc'), ('gold', 'Vàng'), ('platinum', 'Bạch kim')], default='bronze', verbose_name='Cấp độ huy hiệu')

    # Chia sẻ
    is_public = models.BooleanField(default=False, verbose_name='Công khai')
    allow_collaboration = models.BooleanField(default=False, verbose_name='Cho phép cộng tác')

    # Thời gian tạo và cập nhật
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mục tiêu học tập'
        verbose_name_plural = 'Mục tiêu học tập'

    def __str__(self):
        return f"{self.title} ({self.get_goal_type_display()})"

    def save(self, *args, **kwargs):
        # Tính toán phần trăm tiến độ
        if self.target_value > 0:
            self.progress_percentage = min(int((self.current_value / self.target_value) * 100), 100)
        else:
            self.progress_percentage = 0

        # Cập nhật trạng thái
        if self.progress_percentage == 100:
            self.status = 'completed'
        elif timezone.now().date() > self.end_date and self.progress_percentage < 100:
            self.status = 'overdue'
        elif self.current_value > 0:
            self.status = 'in_progress'
        else:
            self.status = 'not_started'

        super().save(*args, **kwargs)

    def update_progress(self, new_value):
        """Cập nhật tiến độ mục tiêu"""
        self.current_value = new_value
        self.save()

        # Tạo bản ghi tiến độ
        GoalProgress.objects.create(
            goal=self,
            value=new_value,
            date=timezone.now().date()
        )

        return self.progress_percentage

    def increment_progress(self, increment=1):
        """Tăng tiến độ mục tiêu"""
        return self.update_progress(self.current_value + increment)

    def is_active(self):
        """Kiểm tra xem mục tiêu có đang hoạt động không"""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date and self.status != 'completed'

    def days_remaining(self):
        """Số ngày còn lại để hoàn thành mục tiêu"""
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days

    def days_since_start(self):
        """Số ngày kể từ khi bắt đầu mục tiêu"""
        today = timezone.now().date()
        if today < self.start_date:
            return 0
        return (today - self.start_date).days

    def total_duration_days(self):
        """Tổng số ngày của mục tiêu"""
        return (self.end_date - self.start_date).days + 1

    def expected_progress(self):
        """Tiến độ dự kiến dựa trên thời gian đã trôi qua"""
        total_days = self.total_duration_days()
        if total_days <= 0:
            return 0

        days_passed = self.days_since_start()
        expected = min(int((days_passed / total_days) * 100), 100)
        return expected

    def is_behind_schedule(self):
        """Kiểm tra xem mục tiêu có đang bị chậm tiến độ không"""
        return self.progress_percentage < self.expected_progress()

class GoalProgress(models.Model):
    """Theo dõi tiến độ đạt mục tiêu"""
    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, related_name='progress_records')
    date = models.DateField(default=timezone.now)
    value = models.PositiveIntegerField(default=0, verbose_name='Giá trị')
    notes = models.TextField(blank=True, verbose_name='Ghi chú')

    class Meta:
        ordering = ['-date']
        verbose_name = 'Tiến độ mục tiêu'
        verbose_name_plural = 'Tiến độ mục tiêu'
        # Đảm bảo mỗi mục tiêu chỉ có một bản ghi tiến độ mỗi ngày
        unique_together = ['goal', 'date']

    def __str__(self):
        return f"{self.goal.title} - {self.date} - {self.value}"

class GoalCollaborator(models.Model):
    """Người cộng tác trong mục tiêu học tập"""

    ROLE_CHOICES = [
        ('viewer', 'Người xem'),
        ('collaborator', 'Người cộng tác'),
        ('admin', 'Quản trị viên'),
    ]

    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, related_name='collaborators')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collaborated_goals')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer', verbose_name='Vai trò')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Người cộng tác'
        verbose_name_plural = 'Người cộng tác'
        unique_together = ['goal', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.goal.title} - {self.get_role_display()}"

class GoalComment(models.Model):
    """Bình luận về mục tiêu học tập"""
    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goal_comments')
    content = models.TextField(verbose_name='Nội dung')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bình luận'
        verbose_name_plural = 'Bình luận'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.goal.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class GoalInvitation(models.Model):
    """Lời mời tham gia mục tiêu học tập"""

    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('accepted', 'Đã chấp nhận'),
        ('declined', 'Đã từ chối'),
    ]

    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, related_name='invitations')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invitations')
    role = models.CharField(max_length=20, choices=GoalCollaborator.ROLE_CHOICES, default='viewer', verbose_name='Vai trò')
    message = models.TextField(blank=True, verbose_name='Lời nhắn')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Trạng thái')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lời mời'
        verbose_name_plural = 'Lời mời'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.username} mời {self.recipient.username} tham gia {self.goal.title}"
