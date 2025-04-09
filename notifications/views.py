from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from .models import Notification, NotificationPreference
from .utils import create_notification

@login_required
def notification_list(request):
    """Hiển thị danh sách thông báo của người dùng"""
    # Lấy tham số từ request
    format_type = request.GET.get('format', '')
    filter_type = request.GET.get('filter', 'all')  # all, unread, read

    # Lấy tất cả thông báo của người dùng
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Lọc theo trạng thái đọc/chưa đọc
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type == 'read':
        notifications = notifications.filter(is_read=True)

    # Phân trang
    paginator = Paginator(notifications, 20)  # 20 thông báo mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Đánh dấu tất cả thông báo đã đọc nếu có tham số mark_all_read
    if 'mark_all_read' in request.GET:
        notifications.filter(is_read=False).update(is_read=True)

        if request.htmx:
            unread_count = notifications.filter(is_read=False).count()
            return JsonResponse({
                'success': True,
                'unread_count': unread_count,
                'message': 'Đã đánh dấu tất cả thông báo là đã đọc'
            })

        messages.success(request, 'Đã đánh dấu tất cả thông báo là đã đọc')
        return redirect('notifications:list')

    # Đếm số thông báo chưa đọc
    unread_count = notifications.filter(is_read=False).count()

    context = {
        'page_obj': page_obj,
        'unread_count': unread_count,
        'filter_type': filter_type,
        'total_count': notifications.count()
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'notifications/notification_list_partial.html', context)

    return render(request, 'notifications/notification_list.html', context)

@login_required
def mark_as_read(request, notification_id):
    """\u0110\u00e1nh d\u1ea5u th\u00f4ng b\u00e1o \u0111\u00e3 \u0111\u1ecdc"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()

    # Đếm số thông báo chưa đọc
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    # Kiểm tra nếu là request HTMX
    if request.htmx:
        context = {
            'notification': notification,
            'unread_count': unread_count
        }
        return render(request, 'notifications/mark_read_response.html', context)

    # Kiểm tra xem yêu cầu có phải là AJAX không
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': unread_count
        })

    # Nếu không phải AJAX hoặc HTMX, chuyển hướng đến URL của thông báo (nếu có)
    if notification.url:
        return redirect(notification.url)

    # Nếu không có URL, quay lại trang danh sách thông báo
    return redirect('notifications:list')

@login_required
def mark_all_as_read(request):
    """\u0110\u00e1nh d\u1ea5u t\u1ea5t c\u1ea3 th\u00f4ng b\u00e1o \u0111\u00e3 \u0111\u1ecdc"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    # Kiểm tra nếu là request HTMX
    if request.htmx:
        context = {
            'unread_count': 0,
            'message': 'Đã đánh dấu tất cả thông báo là đã đọc'
        }
        return render(request, 'notifications/mark_all_read_response.html', context)

    # Kiểm tra xem yêu cầu có phải là AJAX không
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': 0
        })

    messages.success(request, 'Đã đánh dấu tất cả thông báo là đã đọc')
    return redirect('notifications:list')

@login_required
def notification_preferences(request):
    """Quản lý tùy chọn thông báo"""
    # Lấy hoặc tạo tùy chọn thông báo của người dùng
    preferences, created = NotificationPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Cập nhật tùy chọn thông báo
        preferences.receive_realtime_notifications = 'receive_realtime_notifications' in request.POST
        preferences.receive_email_notifications = 'receive_email_notifications' in request.POST

        # Cập nhật tùy chọn loại thông báo
        preferences.email_pomodoro = 'email_pomodoro' in request.POST
        preferences.email_cornell = 'email_cornell' in request.POST
        preferences.email_mindmap = 'email_mindmap' in request.POST
        preferences.email_feynman = 'email_feynman' in request.POST
        preferences.email_project = 'email_project' in request.POST
        preferences.email_exercise = 'email_exercise' in request.POST
        preferences.email_competition = 'email_competition' in request.POST
        preferences.email_system = 'email_system' in request.POST

        # Cập nhật tần suất nhận email
        preferences.email_frequency = request.POST.get('email_frequency', 'immediately')

        preferences.save()

        # Kiểm tra nếu là request HTMX
        if request.htmx:
            return render(request, 'notifications/preferences_response.html')

        messages.success(request, 'Tùy chọn thông báo đã được cập nhật thành công')
        return redirect('notifications:preferences')

    context = {
        'preferences': preferences,
    }

    return render(request, 'notifications/notification_preferences.html', context)

@login_required
def delete_notification(request, notification_id):
    """Xóa thông báo"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()

    # Đếm số thông báo chưa đọc
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    # Kiểm tra nếu là request HTMX
    if request.htmx:
        context = {
            'notification_id': notification_id,
            'unread_count': unread_count,
            'message': 'Thông báo đã được xóa thành công'
        }
        return render(request, 'notifications/delete_response.html', context)

    # Kiểm tra xem yêu cầu có phải là AJAX không
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': unread_count
        })

    messages.success(request, 'Thông báo đã được xóa thành công')
    return redirect('notifications:list')

@login_required
def delete_all_notifications(request):
    """Xóa tất cả thông báo"""
    Notification.objects.filter(user=request.user).delete()

    # Kiểm tra nếu là request HTMX
    if request.htmx:
        context = {
            'message': 'Tất cả thông báo đã được xóa thành công'
        }
        return render(request, 'notifications/delete_all_response.html', context)

    # Kiểm tra xem yêu cầu có phải là AJAX không
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, 'Tất cả thông báo đã được xóa thành công')
    return redirect('notifications:list')

@login_required
def get_unread_count(request):
    """Lấy số lượng thông báo chưa đọc"""
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})
