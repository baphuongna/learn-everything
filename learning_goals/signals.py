from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.urls import reverse

from .models import LearningGoal, GoalProgress, GoalCollaborator, GoalInvitation
from notifications.utils import create_notification

# Thêm import cho hệ thống thành tích
from achievements.signals import check_badge_conditions
from achievements.models import Badge, UserBadge, RewardPoint

@receiver(post_save, sender=LearningGoal)
def goal_created_notification(sender, instance, created, **kwargs):
    """Gửi thông báo khi mục tiêu được tạo"""
    if created:
        create_notification(
            user=instance.user,
            title="Mục tiêu học tập mới",
            message=f"Bạn đã tạo mục tiêu học tập mới: {instance.title}",
            notification_type="info",
            related_feature="system",
            url=f"/learning-goals/{instance.id}/",
            send_email=False
        )

        # Kiểm tra điều kiện nhận huy hiệu
        check_badge_conditions(instance.user, 'goals_created',
                              instance.user.learning_goals.count())

@receiver(post_save, sender=GoalInvitation)
def goal_invitation_notification(sender, instance, created, **kwargs):
    """Gửi thông báo khi có lời mời tham gia mục tiêu"""
    if created:
        # Tạo URL cho các hành động
        accept_url = reverse('learning_goals:handle_invitation', kwargs={'invitation_id': instance.id, 'action': 'accept'})
        decline_url = reverse('learning_goals:handle_invitation', kwargs={'invitation_id': instance.id, 'action': 'decline'})

        # Tạo các nút hành động
        action_buttons = [
            {'text': 'Chấp nhận', 'url': accept_url, 'style': 'success'},
            {'text': 'Từ chối', 'url': decline_url, 'style': 'danger'}
        ]

        # Gửi thông báo cho người nhận lời mời
        create_notification(
            user=instance.recipient,
            title="Lời mời tham gia mục tiêu học tập",
            message=f"{instance.sender.username} đã mời bạn tham gia mục tiêu '{instance.goal.title}' với vai trò {instance.get_role_display()}.",
            notification_type="info",
            related_feature="system",
            related_object_id=instance.id,
            url=f"/learning-goals/{instance.goal.id}/",
            send_email=True,
            action_buttons=action_buttons
        )

@receiver(post_save, sender=GoalCollaborator)
def goal_collaborator_notification(sender, instance, created, **kwargs):
    """Gửi thông báo khi có người tham gia mục tiêu"""
    if created:
        # Gửi thông báo cho chủ sở hữu mục tiêu
        if instance.user != instance.goal.user:
            create_notification(
                user=instance.goal.user,
                title="Người dùng mới tham gia mục tiêu",
                message=f"{instance.user.username} đã tham gia mục tiêu '{instance.goal.title}' của bạn với vai trò {instance.get_role_display()}.",
                notification_type="info",
                related_feature="system",
                url=f"/learning-goals/{instance.goal.id}/",
                send_email=False
            )

@receiver(post_save, sender=GoalProgress)
def goal_progress_notification(sender, instance, created, **kwargs):
    """Gửi thông báo khi tiến độ mục tiêu được cập nhật"""
    if created:
        goal = instance.goal

        # Kiểm tra xem mục tiêu đã hoàn thành chưa
        if goal.progress_percentage == 100:
            create_notification(
                user=goal.user,
                title="Chúc mừng! Mục tiêu đã hoàn thành",
                message=f"Bạn đã hoàn thành mục tiêu: {goal.title}",
                notification_type="success",
                related_feature="system",
                url=f"/learning-goals/{goal.id}/",
                send_email=True
            )

            # Thưởng điểm khi hoàn thành mục tiêu
            reward_point, _ = RewardPoint.objects.get_or_create(user=goal.user)
            reward_point.add_points(
                goal.reward_points,
                f"Hoàn thành mục tiêu: {goal.title}"
            )

            # Tạo huy hiệu tùy chỉnh nếu có
            if goal.has_badge_reward and goal.badge_name:
                # Kiểm tra xem huy hiệu đã tồn tại chưa
                badge, _ = Badge.objects.get_or_create(
                    name=goal.badge_name,
                    defaults={
                        'description': goal.badge_description or f'Hoàn thành mục tiêu: {goal.title}',
                        'category': 'goals',
                        'level': goal.badge_level,
                        'icon': 'fa-bullseye',
                        'points': goal.reward_points,
                        'condition_type': 'custom_goal',
                        'condition_value': 1
                    }
                )

                # Tạo huy hiệu cho người dùng
                user_badge, _ = UserBadge.objects.get_or_create(
                    user=goal.user,
                    badge=badge
                )

            # Kiểm tra điều kiện nhận huy hiệu hệ thống
            completed_goals = LearningGoal.objects.filter(
                user=goal.user,
                status='completed'
            ).count()

            check_badge_conditions(goal.user, 'goals_completed', completed_goals)

            # Thông báo cho người cộng tác nếu có
            if goal.allow_collaboration:
                for collaborator in goal.collaborators.all():
                    create_notification(
                        user=collaborator.user,
                        title=f"Mục tiêu đã hoàn thành",
                        message=f"Mục tiêu '{goal.title}' mà bạn tham gia đã được hoàn thành bởi {goal.user.username}.",
                        notification_type="success",
                        related_feature="system",
                        url=f"/learning-goals/{goal.id}/",
                        send_email=False
                    )

        # Kiểm tra xem mục tiêu đã đạt mốc 50% chưa
        elif goal.progress_percentage >= 50 and (goal.progress_percentage - (instance.value - goal.current_value) / goal.target_value * 100) < 50:
            create_notification(
                user=goal.user,
                title="Đã đạt 50% mục tiêu",
                message=f"Bạn đã hoàn thành 50% mục tiêu: {goal.title}",
                notification_type="info",
                related_feature="system",
                url=f"/learning-goals/{goal.id}/",
                send_email=False
            )
        # Kiểm tra xem mục tiêu đã đạt mốc 75% chưa
        elif goal.progress_percentage >= 75 and (goal.progress_percentage - (instance.value - goal.current_value) / goal.target_value * 100) < 75:
            create_notification(
                user=goal.user,
                title="Đã đạt 75% mục tiêu",
                message=f"Bạn đã hoàn thành 75% mục tiêu: {goal.title}. Cố gắng lên!",
                notification_type="info",
                related_feature="system",
                url=f"/learning-goals/{goal.id}/",
                send_email=False
            )
