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
    reminder_days_before = models.PositiveIntegerField(default=1, verbose_name='Số ngày nhắc trước hạn')
    reminder_time = models.TimeField(default=timezone.now, verbose_name='Thời gian nhắc nhở')
    reminder_email = models.BooleanField(default=True, verbose_name='Gửi nhắc nhở qua email')
    reminder_app = models.BooleanField(default=True, verbose_name='Gửi nhắc nhở trong ứng dụng')
    last_reminder_sent = models.DateTimeField(null=True, blank=True, verbose_name='Lần nhắc nhở gần nhất')

    # Phần thưởng
    reward_points = models.PositiveIntegerField(default=10, verbose_name='Điểm thưởng')
    has_badge_reward = models.BooleanField(default=False, verbose_name='Có huy hiệu thưởng')
    badge_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Tên huy hiệu')
    badge_description = models.TextField(blank=True, null=True, verbose_name='Mô tả huy hiệu')
    badge_level = models.CharField(max_length=20, choices=[('bronze', 'Đồng'), ('silver', 'Bạc'), ('gold', 'Vàng'), ('platinum', 'Bạch kim')], default='bronze', verbose_name='Cấp độ huy hiệu')

    # Chia sẻ
    is_public = models.BooleanField(default=False, verbose_name='Công khai')
    allow_collaboration = models.BooleanField(default=False, verbose_name='Cho phép cộng tác')

    # Mục tiêu lặp lại
    is_recurring = models.BooleanField(default=False, verbose_name='Lặp lại mục tiêu')
    recurring_frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Hàng ngày'),
        ('weekly', 'Hàng tuần'),
        ('monthly', 'Hàng tháng'),
        ('custom', 'Tùy chỉnh')
    ], default='weekly', verbose_name='Tần suất lặp lại')

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
        old_status = self.status
        self.current_value = new_value
        self.save()

        # Tạo bản ghi tiến độ
        GoalProgress.objects.create(
            goal=self,
            value=new_value,
            date=timezone.now().date()
        )

        # Xử lý mục tiêu lặp lại nếu mục tiêu vừa hoàn thành
        if self.status == 'completed' and old_status != 'completed' and self.is_recurring:
            self.create_recurring_goal()

        return self.progress_percentage

    def create_recurring_goal(self):
        """Tạo mục tiêu lặp lại mới"""
        # Tính toán ngày bắt đầu và kết thúc mới
        if self.recurring_frequency == 'daily':
            start_date = self.end_date + timezone.timedelta(days=1)
            end_date = start_date
        elif self.recurring_frequency == 'weekly':
            start_date = self.end_date + timezone.timedelta(days=1)
            end_date = start_date + timezone.timedelta(days=6)
        elif self.recurring_frequency == 'monthly':
            start_date = self.end_date + timezone.timedelta(days=1)
            end_date = start_date + timezone.timedelta(days=29)
        else:  # custom
            start_date = self.end_date + timezone.timedelta(days=1)
            duration = (self.end_date - self.start_date).days
            end_date = start_date + timezone.timedelta(days=duration)

        # Tạo mục tiêu mới
        new_goal = LearningGoal.objects.create(
            user=self.user,
            title=self.title,
            description=self.description,
            goal_type=self.goal_type,
            category=self.category,
            start_date=start_date,
            end_date=end_date,
            target_value=self.target_value,
            current_value=0,
            progress_percentage=0,
            status='not_started',
            subject=self.subject,
            topic=self.topic,
            lesson=self.lesson,
            reminder_enabled=self.reminder_enabled,
            reminder_frequency=self.reminder_frequency,
            reward_points=self.reward_points,
            has_badge_reward=self.has_badge_reward,
            badge_name=self.badge_name,
            badge_description=self.badge_description,
            badge_level=self.badge_level,
            is_public=self.is_public,
            allow_collaboration=self.allow_collaboration,
            is_recurring=self.is_recurring,
            recurring_frequency=self.recurring_frequency
        )

        # Sao chép các cộng tác viên
        for collaborator in self.collaborators.all():
            GoalCollaborator.objects.create(
                goal=new_goal,
                user=collaborator.user,
                role=collaborator.role,
                can_update_progress=collaborator.can_update_progress
            )

        return new_goal

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

    def needs_reminder(self):
        """Kiểm tra xem mục tiêu có cần gửi nhắc nhở không"""
        # Nếu đã hoàn thành hoặc không bật nhắc nhở, không cần gửi
        if self.status == 'completed' or not self.reminder_enabled:
            return False

        today = timezone.now().date()
        current_time = timezone.now().time()

        # Kiểm tra xem đã đến thời gian nhắc nhở chưa
        if current_time < self.reminder_time:
            return False

        # Tính toán ngày cần nhắc nhở
        reminder_date = self.end_date - timezone.timedelta(days=self.reminder_days_before)

        # Nếu hôm nay là ngày cần nhắc nhở
        if today == reminder_date:
            # Kiểm tra xem đã gửi nhắc nhở hôm nay chưa
            if self.last_reminder_sent:
                last_reminder_date = self.last_reminder_sent.date()
                if last_reminder_date == today:
                    return False
            return True

        # Nếu tần suất nhắc nhở là hàng ngày và mục tiêu đang chậm tiến độ
        if self.reminder_frequency == 'daily' and self.is_behind_schedule():
            # Kiểm tra xem đã gửi nhắc nhở hôm nay chưa
            if self.last_reminder_sent:
                last_reminder_date = self.last_reminder_sent.date()
                if last_reminder_date == today:
                    return False
            return True

        # Nếu tần suất nhắc nhở là hàng tuần và mục tiêu đang chậm tiến độ
        if self.reminder_frequency == 'weekly' and self.is_behind_schedule():
            # Kiểm tra xem đã gửi nhắc nhở trong tuần này chưa
            if self.last_reminder_sent:
                days_since_last_reminder = (today - self.last_reminder_sent.date()).days
                if days_since_last_reminder < 7:
                    return False
            return True

        return False

    def send_reminder(self):
        """Gửi nhắc nhở cho mục tiêu"""
        from notifications.models import Notification

        # Cập nhật thời gian gửi nhắc nhở gần nhất
        self.last_reminder_sent = timezone.now()
        self.save(update_fields=['last_reminder_sent'])

        # Tạo thông báo trong ứng dụng
        if self.reminder_app:
            message = f"Mục tiêu '{self.title}' sắp đến hạn và chưa hoàn thành. Tiến độ hiện tại: {self.progress_percentage}%"

            if self.is_behind_schedule():
                message = f"Mục tiêu '{self.title}' đang chậm tiến độ. Tiến độ hiện tại: {self.progress_percentage}%, tiến độ dự kiến: {self.expected_progress()}%"

            Notification.objects.create(
                user=self.user,
                title=f"Nhắc nhở mục tiêu: {self.title}",
                message=message,
                notification_type='goal_reminder',
                related_object_id=self.id,
                related_object_type='learning_goal'
            )

        # Gửi email nhắc nhở (sẽ triển khai sau)
        if self.reminder_email:
            # TODO: Triển khai gửi email nhắc nhở
            pass

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
