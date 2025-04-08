from django.utils import timezone
from django.db.models import F, ExpressionWrapper, fields
from django.db.models.functions import Now
from notifications.utils import create_notification

from .models import LearningGoal

def check_goal_progress():
    """
    Kiểm tra tiến độ mục tiêu và gửi thông báo nhắc nhở cho người dùng
    """
    today = timezone.now().date()
    
    # Lấy các mục tiêu đang hoạt động và chưa hoàn thành
    active_goals = LearningGoal.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        status__in=['not_started', 'in_progress'],
        reminder_enabled=True
    )
    
    for goal in active_goals:
        # Kiểm tra xem mục tiêu có đang chậm tiến độ không
        if goal.is_behind_schedule():
            # Tính số ngày còn lại
            days_remaining = goal.days_remaining()
            
            # Tính phần trăm tiến độ dự kiến
            expected_progress = goal.expected_progress()
            
            # Tính chênh lệch tiến độ
            progress_gap = expected_progress - goal.progress_percentage
            
            # Gửi thông báo nhắc nhở dựa trên mức độ chậm tiến độ
            if days_remaining <= 1:  # Sắp hết hạn (còn 1 ngày hoặc ít hơn)
                create_notification(
                    user=goal.user,
                    title="Mục tiêu sắp hết hạn!",
                    message=f"Mục tiêu '{goal.title}' của bạn sẽ hết hạn trong {days_remaining} ngày. "
                            f"Hiện tại bạn mới hoàn thành {goal.progress_percentage}% (mục tiêu dự kiến: {expected_progress}%). "
                            f"Hãy cố gắng hoàn thành mục tiêu!",
                    notification_type="danger",
                    related_feature="system",
                    url=f"/learning-goals/{goal.id}/",
                    send_email=True
                )
            elif progress_gap >= 30:  # Chậm tiến độ nhiều (>= 30%)
                create_notification(
                    user=goal.user,
                    title="Mục tiêu đang chậm tiến độ nhiều!",
                    message=f"Mục tiêu '{goal.title}' của bạn đang chậm tiến độ {progress_gap:.0f}%. "
                            f"Hiện tại bạn mới hoàn thành {goal.progress_percentage}% (mục tiêu dự kiến: {expected_progress}%). "
                            f"Hãy cố gắng bắt kịp tiến độ!",
                    notification_type="warning",
                    related_feature="system",
                    url=f"/learning-goals/{goal.id}/",
                    send_email=goal.reminder_frequency == 'daily'
                )
            elif progress_gap >= 15:  # Chậm tiến độ vừa phải (>= 15%)
                create_notification(
                    user=goal.user,
                    title="Mục tiêu đang chậm tiến độ!",
                    message=f"Mục tiêu '{goal.title}' của bạn đang chậm tiến độ {progress_gap:.0f}%. "
                            f"Hiện tại bạn mới hoàn thành {goal.progress_percentage}% (mục tiêu dự kiến: {expected_progress}%). "
                            f"Hãy cố gắng bắt kịp tiến độ!",
                    notification_type="info",
                    related_feature="system",
                    url=f"/learning-goals/{goal.id}/",
                    send_email=False
                )

def check_inactive_goals():
    """
    Kiểm tra các mục tiêu không hoạt động và gửi thông báo nhắc nhở
    """
    today = timezone.now().date()
    
    # Lấy các mục tiêu chưa bắt đầu nhưng sắp đến ngày bắt đầu (trong vòng 2 ngày)
    upcoming_goals = LearningGoal.objects.filter(
        start_date__gt=today,
        start_date__lte=today + timezone.timedelta(days=2),
        status='not_started',
        reminder_enabled=True
    )
    
    for goal in upcoming_goals:
        # Tính số ngày còn lại đến khi bắt đầu
        days_until_start = (goal.start_date - today).days
        
        # Gửi thông báo nhắc nhở
        create_notification(
            user=goal.user,
            title="Mục tiêu sắp bắt đầu!",
            message=f"Mục tiêu '{goal.title}' của bạn sẽ bắt đầu trong {days_until_start} ngày. "
                    f"Hãy chuẩn bị sẵn sàng!",
            notification_type="info",
            related_feature="system",
            url=f"/learning-goals/{goal.id}/",
            send_email=False
        )
    
    # Lấy các mục tiêu đã quá hạn nhưng chưa được đánh dấu là quá hạn
    overdue_goals = LearningGoal.objects.filter(
        end_date__lt=today,
        status__in=['not_started', 'in_progress']
    )
    
    for goal in overdue_goals:
        # Cập nhật trạng thái mục tiêu
        goal.status = 'overdue'
        goal.save()
        
        # Gửi thông báo nhắc nhở
        if goal.reminder_enabled:
            create_notification(
                user=goal.user,
                title="Mục tiêu đã quá hạn!",
                message=f"Mục tiêu '{goal.title}' của bạn đã quá hạn. "
                        f"Hiện tại bạn mới hoàn thành {goal.progress_percentage}%. "
                        f"Bạn có thể chỉnh sửa ngày kết thúc hoặc đánh dấu mục tiêu là đã hoàn thành.",
                notification_type="danger",
                related_feature="system",
                url=f"/learning-goals/{goal.id}/",
                send_email=True
            )
