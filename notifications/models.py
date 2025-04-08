from django.db import models
from django.contrib.auth.models import User

class NotificationPreference(models.Model):
    """Tùy chọn thông báo của người dùng"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')

    # Tùy chọn thông báo trong ứng dụng
    receive_realtime_notifications = models.BooleanField(default=True, help_text='Nhận thông báo thời gian thực trong ứng dụng')

    # Tùy chọn thông báo qua email
    receive_email_notifications = models.BooleanField(default=True, help_text='Nhận thông báo qua email')

    # Tùy chọn loại thông báo
    email_pomodoro = models.BooleanField(default=False, help_text='Nhận email về Pomodoro Timer')
    email_cornell = models.BooleanField(default=False, help_text='Nhận email về Cornell Notes')
    email_mindmap = models.BooleanField(default=False, help_text='Nhận email về Mind Mapping')
    email_feynman = models.BooleanField(default=False, help_text='Nhận email về Feynman Technique')
    email_project = models.BooleanField(default=True, help_text='Nhận email về Project-Based Learning')
    email_exercise = models.BooleanField(default=False, help_text='Nhận email về Interactive Exercises')
    email_competition = models.BooleanField(default=True, help_text='Nhận email về Competition Mode')
    email_system = models.BooleanField(default=True, help_text='Nhận email về hệ thống')

    # Tần suất nhận email
    email_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediately', 'Ngay lập tức'),
            ('daily', 'Hàng ngày'),
            ('weekly', 'Hàng tuần'),
        ],
        default='immediately',
        help_text='Tần suất nhận email thông báo'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification Preferences for {self.user.username}"

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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    related_feature = models.CharField(max_length=20, choices=RELATED_FEATURES, default='system')
    related_object_id = models.IntegerField(null=True, blank=True)  # ID của đối tượng liên quan (nếu có)
    url = models.CharField(max_length=200, blank=True)  # URL để chuyển hướng khi nhấp vào thông báo
    is_read = models.BooleanField(default=False)  # Đánh dấu đã đọc hay chưa

    # Trạng thái gửi email
    email_sent = models.BooleanField(default=False)  # Đánh dấu đã gửi email hay chưa
    email_sent_at = models.DateTimeField(null=True, blank=True)  # Thời điểm gửi email

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"
