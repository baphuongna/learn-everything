import json
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, NotificationPreference

def create_notification(user, title, message, notification_type='info', related_feature='system',
                       related_object_id=None, url='', send_email=False, action_buttons=None):
    """
    Tạo thông báo mới và gửi qua WebSocket nếu người dùng đang online

    Args:
        user: Người dùng nhận thông báo
        title: Tiêu đề thông báo
        message: Nội dung thông báo
        notification_type: Loại thông báo (info, success, warning, danger)
        related_feature: Tính năng liên quan (pomodoro, cornell, mindmap, feynman, project, exercise, competition, system)
        related_object_id: ID của đối tượng liên quan (nếu có)
        url: URL để chuyển hướng khi nhấp vào thông báo
        send_email: Có gửi email thông báo hay không
        action_buttons: Danh sách các nút hành động (dict với keys: 'text', 'url', 'style')

    Returns:
        Notification: Đối tượng thông báo đã tạo
    """
    # Tạo thông báo mới
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        related_feature=related_feature,
        related_object_id=related_object_id,
        url=url,
        data=json.dumps({'action_buttons': action_buttons}) if action_buttons else None
    )

    # Gửi thông báo qua WebSocket nếu người dùng đang online
    try:
        # Kiểm tra tùy chọn thông báo của người dùng
        preferences, created = NotificationPreference.objects.get_or_create(user=user)

        if preferences.receive_realtime_notifications:
            channel_layer = get_channel_layer()
            notification_data = {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.notification_type,
                "feature": notification.related_feature,
                "url": notification.url,
                "created_at": notification.created_at.isoformat(),
            }

            async_to_sync(channel_layer.group_send)(
                f"notifications_{user.id}",
                {
                    "type": "notification_message",
                    "notification": notification_data
                }
            )
    except Exception as e:
        print(f"Error sending WebSocket notification: {e}")

    # Gửi email thông báo nếu được yêu cầu và người dùng đã bật tùy chọn nhận email
    if send_email:
        try:
            send_notification_email(notification)
        except Exception as e:
            print(f"Error sending email notification: {e}")

    return notification

def send_notification_email(notification):
    """
    Gửi email thông báo cho người dùng

    Args:
        notification: Đối tượng thông báo cần gửi email

    Returns:
        bool: True nếu gửi thành công, False nếu không
    """
    # Kiểm tra tùy chọn thông báo của người dùng
    try:
        preferences, created = NotificationPreference.objects.get_or_create(user=notification.user)

        # Kiểm tra xem người dùng có muốn nhận email không
        if not preferences.receive_email_notifications:
            return False

        # Kiểm tra tùy chọn loại thông báo
        feature_preference = getattr(preferences, f"email_{notification.related_feature}", False)
        if not feature_preference:
            return False

        # Kiểm tra tần suất gửi email
        if preferences.email_frequency != 'immediately':
            # Đánh dấu thông báo cần gửi email sau
            notification.email_sent = False
            notification.save()
            return False

        # Chuẩn bị nội dung email
        context = {
            'user': notification.user,
            'notification': notification,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        }

        # Render template email
        html_message = render_to_string('notifications/email/notification_email.html', context)
        plain_message = render_to_string('notifications/email/notification_email.txt', context)

        # Gửi email
        send_mail(
            subject=notification.title,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        # Cập nhật trạng thái gửi email
        notification.email_sent = True
        notification.email_sent_at = timezone.now()
        notification.save()

        return True

    except Exception as e:
        print(f"Error sending notification email: {e}")
        return False

def send_daily_email_notifications():
    """Gửi email thông báo hàng ngày cho người dùng đã chọn tần suất 'daily'"""
    # Lấy danh sách người dùng đã chọn tần suất 'daily'
    preferences = NotificationPreference.objects.filter(
        receive_email_notifications=True,
        email_frequency='daily'
    )

    for pref in preferences:
        # Lấy thông báo chưa gửi email của người dùng
        notifications = Notification.objects.filter(
            user=pref.user,
            email_sent=False,
            created_at__gte=timezone.now() - timezone.timedelta(days=1)
        )

        if notifications.exists():
            # Chuẩn bị nội dung email
            context = {
                'user': pref.user,
                'notifications': notifications,
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
            }

            # Render template email
            html_message = render_to_string('notifications/email/daily_notifications.html', context)
            plain_message = render_to_string('notifications/email/daily_notifications.txt', context)

            # Gửi email
            try:
                send_mail(
                    subject=f"Thông báo hàng ngày từ Nền Tảng Học Tập",
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[pref.user.email],
                    html_message=html_message,
                    fail_silently=False,
                )

                # Cập nhật trạng thái gửi email
                notifications.update(email_sent=True, email_sent_at=timezone.now())

            except Exception as e:
                print(f"Error sending daily notification email to {pref.user.email}: {e}")

def send_weekly_email_notifications():
    """Gửi email thông báo hàng tuần cho người dùng đã chọn tần suất 'weekly'"""
    # Lấy danh sách người dùng đã chọn tần suất 'weekly'
    preferences = NotificationPreference.objects.filter(
        receive_email_notifications=True,
        email_frequency='weekly'
    )

    for pref in preferences:
        # Lấy thông báo chưa gửi email của người dùng
        notifications = Notification.objects.filter(
            user=pref.user,
            email_sent=False,
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        )

        if notifications.exists():
            # Chuẩn bị nội dung email
            context = {
                'user': pref.user,
                'notifications': notifications,
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
            }

            # Render template email
            html_message = render_to_string('notifications/email/weekly_notifications.html', context)
            plain_message = render_to_string('notifications/email/weekly_notifications.txt', context)

            # Gửi email
            try:
                send_mail(
                    subject=f"Thông báo hàng tuần từ Nền Tảng Học Tập",
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[pref.user.email],
                    html_message=html_message,
                    fail_silently=False,
                )

                # Cập nhật trạng thái gửi email
                notifications.update(email_sent=True, email_sent_at=timezone.now())

            except Exception as e:
                print(f"Error sending weekly notification email to {pref.user.email}: {e}")
