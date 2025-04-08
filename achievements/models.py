from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator

class Badge(models.Model):
    """Huy hiệu thành tích"""

    BADGE_CATEGORIES = [
        ('learning', 'Học tập'),
        ('goals', 'Mục tiêu'),
        ('flashcards', 'Flashcards'),
        ('quizzes', 'Bài kiểm tra'),
        ('projects', 'Dự án'),
        ('special', 'Đặc biệt'),
    ]

    BADGE_LEVELS = [
        ('bronze', 'Đồng'),
        ('silver', 'Bạc'),
        ('gold', 'Vàng'),
        ('platinum', 'Bạch kim'),
    ]

    name = models.CharField(max_length=100, verbose_name='Tên huy hiệu')
    description = models.TextField(verbose_name='Mô tả')
    category = models.CharField(max_length=20, choices=BADGE_CATEGORIES, default='learning', verbose_name='Danh mục')
    level = models.CharField(max_length=20, choices=BADGE_LEVELS, default='bronze', verbose_name='Cấp độ')
    icon = models.CharField(max_length=50, default='fa-award', verbose_name='Biểu tượng')
    points = models.PositiveIntegerField(default=10, verbose_name='Điểm thưởng')

    # Điều kiện đạt được huy hiệu
    condition_type = models.CharField(max_length=100, verbose_name='Loại điều kiện')
    condition_value = models.PositiveIntegerField(default=1, verbose_name='Giá trị điều kiện')

    # Thời gian tạo và cập nhật
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Huy hiệu'
        verbose_name_plural = 'Huy hiệu'
        ordering = ['category', 'level', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

    def get_icon_class(self):
        """Lấy class biểu tượng đầy đủ"""
        return f"fas {self.icon}"

    def get_level_color(self):
        """Lấy màu sắc tương ứng với cấp độ huy hiệu"""
        colors = {
            'bronze': '#cd7f32',
            'silver': '#c0c0c0',
            'gold': '#ffd700',
            'platinum': '#e5e4e2',
        }
        return colors.get(self.level, '#000000')

class UserBadge(models.Model):
    """Huy hiệu của người dùng"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='user_badges')
    earned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Huy hiệu người dùng'
        verbose_name_plural = 'Huy hiệu người dùng'
        ordering = ['-earned_at']
        # Đảm bảo mỗi người dùng chỉ có một huy hiệu cụ thể
        unique_together = ['user', 'badge']

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"

class RewardPoint(models.Model):
    """Điểm thưởng của người dùng"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reward_points')
    points = models.PositiveIntegerField(default=0, verbose_name='Điểm thưởng')
    lifetime_points = models.PositiveIntegerField(default=0, verbose_name='Tổng điểm thưởng')

    class Meta:
        verbose_name = 'Điểm thưởng'
        verbose_name_plural = 'Điểm thưởng'

    def __str__(self):
        return f"{self.user.username} - {self.points} điểm"

    def add_points(self, points, reason=None):
        """Thêm điểm thưởng cho người dùng"""
        self.points += points
        self.lifetime_points += points
        self.save()

        # Tạo lịch sử điểm thưởng
        PointHistory.objects.create(
            user=self.user,
            points=points,
            action_type='earn',
            reason=reason or 'Thêm điểm thưởng'
        )

        return self.points

    def use_points(self, points, reason=None):
        """Sử dụng điểm thưởng của người dùng"""
        if points > self.points:
            raise ValueError("Không đủ điểm thưởng")

        self.points -= points
        self.save()

        # Tạo lịch sử điểm thưởng
        PointHistory.objects.create(
            user=self.user,
            points=points,
            action_type='use',
            reason=reason or 'Sử dụng điểm thưởng'
        )

        return self.points

class PointHistory(models.Model):
    """Lịch sử điểm thưởng"""
    ACTION_TYPES = [
        ('earn', 'Nhận điểm'),
        ('use', 'Sử dụng điểm'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_history')
    points = models.PositiveIntegerField(verbose_name='Số điểm')
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES, verbose_name='Loại hành động')
    reason = models.CharField(max_length=255, verbose_name='Lý do')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lịch sử điểm thưởng'
        verbose_name_plural = 'Lịch sử điểm thưởng'
        ordering = ['-timestamp']

    def __str__(self):
        action = "Nhận" if self.action_type == 'earn' else "Sử dụng"
        return f"{self.user.username} - {action} {self.points} điểm - {self.reason}"

class Reward(models.Model):
    """Phần thưởng có thể đổi bằng điểm thưởng"""
    name = models.CharField(max_length=100, verbose_name='Tên phần thưởng')
    description = models.TextField(verbose_name='Mô tả')
    points_required = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name='Điểm yêu cầu')
    icon = models.CharField(max_length=50, default='fa-gift', verbose_name='Biểu tượng')
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')

    # Thời gian tạo và cập nhật
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Phần thưởng'
        verbose_name_plural = 'Phần thưởng'
        ordering = ['points_required', 'name']

    def __str__(self):
        return f"{self.name} ({self.points_required} điểm)"

    def get_icon_class(self):
        """Lấy class biểu tượng đầy đủ"""
        return f"fas {self.icon}"

class UserReward(models.Model):
    """Phần thưởng của người dùng"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, related_name='user_rewards')
    redeemed_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False, verbose_name='Đã sử dụng')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='Thời gian sử dụng')

    class Meta:
        verbose_name = 'Phần thưởng người dùng'
        verbose_name_plural = 'Phần thưởng người dùng'
        ordering = ['-redeemed_at']

    def __str__(self):
        return f"{self.user.username} - {self.reward.name}"

    def use_reward(self):
        """Đánh dấu phần thưởng đã được sử dụng"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()

        return True