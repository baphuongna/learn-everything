from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from notifications.utils import create_notification

from .models import Badge, UserBadge, RewardPoint, PointHistory, Reward, UserReward

@receiver(post_save, sender=User)
def create_reward_points(sender, instance, created, **kwargs):
    """Tạo điểm thưởng cho người dùng mới"""
    if created:
        RewardPoint.objects.create(user=instance)

@receiver(post_save, sender=UserBadge)
def badge_earned_notification(sender, instance, created, **kwargs):
    """Gửi thông báo khi người dùng nhận được huy hiệu mới"""
    if created:
        # Thêm điểm thưởng cho người dùng
        reward_point, _ = RewardPoint.objects.get_or_create(user=instance.user)
        reward_point.add_points(
            instance.badge.points,
            f"Nhận huy hiệu {instance.badge.name}"
        )
        
        # Gửi thông báo
        create_notification(
            user=instance.user,
            title=f"Chúc mừng! Bạn đã nhận được huy hiệu {instance.badge.name}",
            message=f"Bạn đã nhận được huy hiệu {instance.badge.name} ({instance.badge.get_level_display()}) "
                    f"và {instance.badge.points} điểm thưởng. {instance.badge.description}",
            notification_type="success",
            related_feature="system",
            url="/achievements/badges/",
            send_email=True
        )

@receiver(post_save, sender=UserReward)
def reward_redeemed_notification(sender, instance, created, **kwargs):
    """Gửi thông báo khi người dùng đổi phần thưởng"""
    if created:
        # Gửi thông báo
        create_notification(
            user=instance.user,
            title=f"Bạn đã đổi phần thưởng {instance.reward.name}",
            message=f"Bạn đã sử dụng {instance.reward.points_required} điểm thưởng để đổi lấy {instance.reward.name}. "
                    f"Bạn có thể xem phần thưởng của mình trong trang Thành tích.",
            notification_type="info",
            related_feature="system",
            url="/achievements/rewards/",
            send_email=False
        )

def check_badge_conditions(user, condition_type, value=1):
    """
    Kiểm tra điều kiện để nhận huy hiệu
    
    Args:
        user: Người dùng cần kiểm tra
        condition_type: Loại điều kiện (ví dụ: 'goals_completed', 'flashcards_reviewed')
        value: Giá trị hiện tại (mặc định là 1, dùng cho các sự kiện đơn lẻ)
    """
    # Lấy tất cả các huy hiệu có điều kiện phù hợp
    badges = Badge.objects.filter(condition_type=condition_type)
    
    # Lấy các huy hiệu mà người dùng đã có
    user_badges = UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
    
    # Kiểm tra từng huy hiệu
    for badge in badges:
        # Bỏ qua nếu người dùng đã có huy hiệu này
        if badge.id in user_badges:
            continue
        
        # Kiểm tra xem người dùng có đạt điều kiện không
        if value >= badge.condition_value:
            # Tạo huy hiệu cho người dùng
            UserBadge.objects.create(
                user=user,
                badge=badge,
                earned_at=timezone.now()
            )
