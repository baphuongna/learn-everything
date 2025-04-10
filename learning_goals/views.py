from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Avg, Count, Q
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.forms import modelformset_factory

from .models import LearningGoal, GoalProgress, GoalCollaborator, GoalComment, GoalInvitation
from .forms import LearningGoalForm, GoalProgressForm, GoalInvitationForm, GoalCommentForm, ReminderSettingsForm
from .utils import generate_ical_for_goal, generate_google_calendar_link

@login_required
def export_goal_ical(request, goal_id):
    """Xuất mục tiêu sang định dạng iCalendar"""
    goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)

    # Tạo file iCalendar
    ical_data = generate_ical_for_goal(goal)

    # Tạo response
    response = HttpResponse(ical_data, content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="{goal.title}.ics"'

    return response

@login_required
def goal_list(request):
    """Hiển thị danh sách mục tiêu học tập của người dùng"""
    # Lọc theo loại mục tiêu
    goal_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    format_type = request.GET.get('format', '')
    recurring = request.GET.get('recurring', '')

    # Lấy danh sách mục tiêu
    goals = LearningGoal.objects.filter(user=request.user)

    # Áp dụng bộ lọc
    if goal_type:
        goals = goals.filter(goal_type=goal_type)
    if status:
        goals = goals.filter(status=status)
    if recurring == 'true':
        goals = goals.filter(is_recurring=True)

    # Phân loại mục tiêu
    daily_goals = goals.filter(goal_type='daily')
    weekly_goals = goals.filter(goal_type='weekly')
    monthly_goals = goals.filter(goal_type='monthly')

    # Thống kê
    total_goals = goals.count()
    completed_goals = goals.filter(status='completed').count()
    active_goals = goals.filter(status__in=['not_started', 'in_progress']).count()
    overdue_goals = goals.filter(status='overdue').count()

    completion_rate = 0
    if total_goals > 0:
        completion_rate = int((completed_goals / total_goals) * 100)

    # Sắp xếp mục tiêu
    sort_by = request.GET.get('sort', 'end_date')
    if sort_by == 'priority':
        goals = goals.order_by('-priority', 'end_date')
    elif sort_by == 'progress':
        goals = goals.order_by('-progress_percentage', 'end_date')
    elif sort_by == 'created':
        goals = goals.order_by('-created_at')
    else:  # end_date
        goals = goals.order_by('end_date')

    context = {
        'goals': goals,
        'daily_goals': daily_goals,
        'weekly_goals': weekly_goals,
        'monthly_goals': monthly_goals,
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'active_goals': active_goals,
        'overdue_goals': overdue_goals,
        'completion_rate': completion_rate,
        'selected_type': goal_type,
        'selected_status': status,
        'sort_by': sort_by,
        'is_recurring_filter': recurring == 'true'
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'learning_goals/goal_list_partial.html', context)

    return render(request, 'learning_goals/goal_list.html', context)

@login_required
def goal_detail(request, goal_id):
    """Hiển thị chi tiết mục tiêu học tập"""
    # Lấy tham số từ request
    format_type = request.GET.get('format', '')
    section = request.GET.get('section', '')

    # Kiểm tra xem người dùng có quyền truy cập mục tiêu không
    goal = get_object_or_404(LearningGoal, id=goal_id)

    # Kiểm tra quyền truy cập
    if goal.user != request.user:
        # Nếu không phải chủ sở hữu, kiểm tra xem có phải người cộng tác không
        if not goal.is_public and not goal.collaborators.filter(user=request.user).exists():
            messages.error(request, 'Bạn không có quyền truy cập mục tiêu này')
            return redirect('learning_goals:goal_list')

    # Lấy lịch sử tiến độ
    progress_history = goal.progress_records.all().order_by('date')

    # Lấy danh sách người cộng tác
    collaborators = goal.collaborators.all().select_related('user')

    # Lấy bình luận
    comments = goal.comments.all().order_by('-created_at').select_related('user')

    # Form cập nhật tiến độ
    progress_form = None
    comment_form = None
    invitation_form = None

    # Kiểm tra xem người dùng có quyền cập nhật tiến độ không
    can_update_progress = (goal.user == request.user) or goal.collaborators.filter(user=request.user, role__in=['collaborator', 'admin']).exists()

    # Kiểm tra xem người dùng có quyền mời người khác không
    can_invite = (goal.user == request.user) or goal.collaborators.filter(user=request.user, role='admin').exists()

    # Xử lý form cập nhật tiến độ
    if can_update_progress:
        if 'update_progress' in request.POST:
            progress_form = GoalProgressForm(request.POST)
            if progress_form.is_valid():
                new_value = progress_form.cleaned_data['value']
                notes = progress_form.cleaned_data['notes']

                # Cập nhật tiến độ
                goal.update_progress(new_value)

                # Cập nhật ghi chú cho bản ghi tiến độ mới nhất
                latest_progress = goal.progress_records.latest('date')
                latest_progress.notes = notes
                latest_progress.save()

                if request.htmx:
                    context = {
                        'goal': goal,
                        'progress_history': progress_history,
                        'days_remaining': goal.days_remaining(),
                        'expected_progress': goal.expected_progress(),
                        'is_behind': goal.is_behind_schedule(),
                    }
                    return render(request, 'learning_goals/goal_progress_updated.html', context)

                messages.success(request, 'Tiến độ đã được cập nhật thành công!')
                return redirect('learning_goals:goal_detail', goal_id=goal.id)
        else:
            progress_form = GoalProgressForm(initial={'value': goal.current_value})

    # Xử lý form bình luận
    if 'add_comment' in request.POST:
        comment_form = GoalCommentForm(request.POST)
        if comment_form.is_valid():
            content = comment_form.cleaned_data['content']

            # Tạo bình luận mới
            comment = GoalComment.objects.create(
                goal=goal,
                user=request.user,
                content=content
            )

            if request.htmx:
                context = {
                    'comment': comment,
                    'goal': goal,
                }
                return render(request, 'learning_goals/comment_added.html', context)

            messages.success(request, 'Bình luận đã được thêm thành công!')
            return redirect('learning_goals:goal_detail', goal_id=goal.id)
    else:
        comment_form = GoalCommentForm()

    # Xử lý form mời người dùng
    if can_invite and 'send_invitation' in request.POST:
        invitation_form = GoalInvitationForm(request.POST)
        if invitation_form.is_valid():
            username = invitation_form.cleaned_data['username']
            role = invitation_form.cleaned_data['role']
            message = invitation_form.cleaned_data['message']

            # Lấy người dùng được mời
            recipient = User.objects.get(username=username)

            # Kiểm tra xem người dùng đã là người cộng tác chưa
            if goal.collaborators.filter(user=recipient).exists():
                messages.error(request, f'Người dùng {username} đã là người cộng tác của mục tiêu này')
            # Kiểm tra xem đã gửi lời mời chưa
            elif goal.invitations.filter(recipient=recipient, status='pending').exists():
                messages.error(request, f'Bạn đã gửi lời mời cho người dùng {username} rồi')
            else:
                # Tạo lời mời mới
                invitation = GoalInvitation.objects.create(
                    goal=goal,
                    sender=request.user,
                    recipient=recipient,
                    role=role,
                    message=message
                )

                if request.htmx:
                    context = {
                        'invitation': invitation,
                        'goal': goal,
                    }
                    return render(request, 'learning_goals/invitation_sent.html', context)

                messages.success(request, f'Lời mời đã được gửi đến {username}')
                return redirect('learning_goals:goal_detail', goal_id=goal.id)
    else:
        invitation_form = GoalInvitationForm()

    # Tạo link Google Calendar
    google_calendar_link = generate_google_calendar_link(goal)

    context = {
        'goal': goal,
        'progress_history': progress_history,
        'progress_form': progress_form,
        'comment_form': comment_form,
        'invitation_form': invitation_form,
        'days_remaining': goal.days_remaining(),
        'expected_progress': goal.expected_progress(),
        'is_behind': goal.is_behind_schedule(),
        'google_calendar_link': google_calendar_link,
        'collaborators': collaborators,
        'comments': comments,
        'can_update_progress': can_update_progress,
        'can_invite': can_invite,
        'is_owner': goal.user == request.user,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        if section == 'progress':
            return render(request, 'learning_goals/goal_progress_partial.html', context)
        elif section == 'comments':
            return render(request, 'learning_goals/goal_comments_partial.html', context)
        elif section == 'collaborators':
            return render(request, 'learning_goals/goal_collaborators_partial.html', context)
        else:
            return render(request, 'learning_goals/goal_detail_partial.html', context)

    return render(request, 'learning_goals/goal_detail.html', context)

@login_required
def goal_create(request):
    """Tạo mục tiêu học tập mới"""
    # Xử lý tham số recurring
    recurring = request.GET.get('recurring', '')

    # Đặt giá trị mặc định cho ngày bắt đầu và kết thúc
    today = timezone.now().date()

    # Mặc định là mục tiêu hàng tuần
    end_date = today + timezone.timedelta(days=6)
    goal_type = 'weekly'

    # Khởi tạo dữ liệu ban đầu
    initial_data = {
        'start_date': today,
        'end_date': end_date,
        'goal_type': goal_type,
    }

    # Xử lý tham số recurring
    if recurring in ['daily', 'weekly', 'monthly']:
        initial_data['is_recurring'] = True
        initial_data['recurring_frequency'] = recurring
        initial_data['goal_type'] = recurring

        # Cập nhật ngày kết thúc dựa trên loại mục tiêu
        if recurring == 'daily':
            initial_data['end_date'] = today
        elif recurring == 'weekly':
            initial_data['end_date'] = today + timezone.timedelta(days=6)
        elif recurring == 'monthly':
            initial_data['end_date'] = today + timezone.timedelta(days=29)

    if request.method == 'POST':
        form = LearningGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()

            messages.success(request, 'Mục tiêu học tập đã được tạo thành công!')
            return redirect('learning_goals:goal_detail', goal_id=goal.id)
    else:
        form = LearningGoalForm(initial=initial_data)

    context = {
        'form': form,
        'title': 'Tạo Mục Tiêu Học Tập Mới',
        'button_text': 'Tạo Mục Tiêu',
    }

    return render(request, 'learning_goals/goal_form.html', context)

@login_required
def goal_edit(request, goal_id):
    """Chỉnh sửa mục tiêu học tập"""
    goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)

    if request.method == 'POST':
        form = LearningGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()

            messages.success(request, 'Mục tiêu học tập đã được cập nhật thành công!')
            return redirect('learning_goals:goal_detail', goal_id=goal.id)
    else:
        form = LearningGoalForm(instance=goal)

    context = {
        'form': form,
        'goal': goal,
        'title': 'Chỉnh Sửa Mục Tiêu Học Tập',
        'button_text': 'Cập Nhật Mục Tiêu',
    }

    return render(request, 'learning_goals/goal_form.html', context)

@login_required
@require_POST
def goal_delete(request, goal_id):
    """Xóa mục tiêu học tập"""
    goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)
    goal.delete()

    messages.success(request, 'Mục tiêu học tập đã được xóa thành công!')
    return redirect('learning_goals:goal_list')

@login_required
def update_progress(request, goal_id):
    """Cập nhật tiến độ mục tiêu (AJAX/HTMX)"""
    goal = get_object_or_404(LearningGoal, id=goal_id)

    # Kiểm tra quyền truy cập
    can_update_progress = (goal.user == request.user) or goal.collaborators.filter(user=request.user, role__in=['collaborator', 'admin']).exists()

    if not can_update_progress:
        if request.htmx:
            return render(request, 'learning_goals/error_message.html', {
                'message': 'Bạn không có quyền cập nhật tiến độ của mục tiêu này'
            })
        return JsonResponse({
            'success': False,
            'error': 'Bạn không có quyền cập nhật tiến độ của mục tiêu này',
        })

    try:
        new_value = int(request.POST.get('value', 0))
        notes = request.POST.get('notes', '')

        # Cập nhật tiến độ
        progress_percentage = goal.update_progress(new_value)

        # Cập nhật ghi chú cho bản ghi tiến độ mới nhất
        latest_progress = goal.progress_records.latest('date')
        latest_progress.notes = notes
        latest_progress.save()

        # Lấy lịch sử tiến độ
        progress_history = goal.progress_records.all().order_by('date')

        # Kiểm tra nếu là request HTMX
        if request.htmx:
            context = {
                'goal': goal,
                'progress_history': progress_history,
                'days_remaining': goal.days_remaining(),
                'expected_progress': goal.expected_progress(),
                'is_behind': goal.is_behind_schedule(),
            }
            return render(request, 'learning_goals/goal_progress_updated.html', context)

        return JsonResponse({
            'success': True,
            'progress': progress_percentage,
            'current_value': goal.current_value,
            'status': goal.status,
            'status_display': goal.get_status_display(),
        })
    except Exception as e:
        if request.htmx:
            return render(request, 'learning_goals/error_message.html', {
                'message': f'Lỗi: {str(e)}'
            })
        return JsonResponse({
            'success': False,
            'error': str(e),
        })

@login_required
def goal_dashboard(request):
    """Trang tổng quan mục tiêu học tập"""
    # Lấy tham số từ request
    format_type = request.GET.get('format', '')
    section = request.GET.get('section', '')

    # Lấy tất cả mục tiêu của người dùng
    goals = LearningGoal.objects.filter(user=request.user)

    # Thống kê tổng quan
    total_goals = goals.count()
    completed_goals = goals.filter(status='completed').count()
    active_goals = goals.filter(status__in=['not_started', 'in_progress']).count()
    overdue_goals = goals.filter(status='overdue').count()
    recurring_goals = goals.filter(is_recurring=True).count()

    # Tỷ lệ hoàn thành
    completion_rate = 0
    if total_goals > 0:
        completion_rate = int((completed_goals / total_goals) * 100)

    # Mục tiêu theo loại
    daily_goals = goals.filter(goal_type='daily')
    weekly_goals = goals.filter(goal_type='weekly')
    monthly_goals = goals.filter(goal_type='monthly')

    # Mục tiêu theo danh mục
    category_stats = goals.values('category').annotate(
        count=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        avg_progress=Avg('progress_percentage')
    )

    # Mục tiêu đang hoạt động
    active_goals_list = goals.filter(status__in=['not_started', 'in_progress']).order_by('end_date')[:5]

    # Mục tiêu gần đến hạn
    upcoming_deadlines = goals.filter(
        status__in=['not_started', 'in_progress'],
        end_date__gte=timezone.now().date()
    ).order_by('end_date')[:5]

    # Mục tiêu mới hoàn thành
    recently_completed = goals.filter(status='completed').order_by('-updated_at')[:5]

    context = {
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'active_goals': active_goals,
        'overdue_goals': overdue_goals,
        'recurring_goals': recurring_goals,
        'completion_rate': completion_rate,
        'daily_goals': daily_goals,
        'weekly_goals': weekly_goals,
        'monthly_goals': monthly_goals,
        'category_stats': category_stats,
        'active_goals_list': active_goals_list,
        'upcoming_deadlines': upcoming_deadlines,
        'recently_completed': recently_completed,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        if section == 'stats':
            return render(request, 'learning_goals/dashboard_stats_partial.html', context)
        elif section == 'active_goals':
            return render(request, 'learning_goals/dashboard_active_goals_partial.html', context)
        elif section == 'upcoming_deadlines':
            return render(request, 'learning_goals/dashboard_upcoming_deadlines_partial.html', context)
        elif section == 'recently_completed':
            return render(request, 'learning_goals/dashboard_recently_completed_partial.html', context)
        else:
            return render(request, 'learning_goals/goal_dashboard_partial.html', context)

    return render(request, 'learning_goals/goal_dashboard.html', context)

@login_required
def update_progress(request, goal_id):
    """Cập nhật tiến độ mục tiêu"""
    goal = get_object_or_404(LearningGoal, id=goal_id)

    # Kiểm tra quyền cập nhật tiến độ
    can_update = (goal.user == request.user) or goal.collaborators.filter(user=request.user, role__in=['collaborator', 'admin']).exists()

    if not can_update:
        messages.error(request, 'Bạn không có quyền cập nhật tiến độ mục tiêu này')
        return redirect('learning_goals:goal_detail', goal_id=goal.id)

    if request.method == 'POST':
        form = GoalProgressForm(request.POST)
        if form.is_valid():
            new_value = form.cleaned_data['value']
            notes = form.cleaned_data['notes']

            # Cập nhật tiến độ
            goal.update_progress(new_value)

            # Cập nhật ghi chú cho bản ghi tiến độ mới nhất
            latest_progress = goal.progress_records.latest('date')
            latest_progress.notes = notes
            latest_progress.save()

            messages.success(request, 'Tiến độ đã được cập nhật thành công!')
            return redirect('learning_goals:goal_detail', goal_id=goal.id)
    else:
        form = GoalProgressForm(initial={'value': goal.current_value})

    return render(request, 'learning_goals/update_progress.html', {
        'goal': goal,
        'form': form
    })

@login_required
def handle_invitation(request, invitation_id, action):
    """Xử lý lời mời tham gia mục tiêu"""
    invitation = get_object_or_404(GoalInvitation, id=invitation_id, recipient=request.user, status='pending')

    if action == 'accept':
        # Chấp nhận lời mời
        invitation.status = 'accepted'
        invitation.save()

        # Tạo người cộng tác mới
        collaborator = GoalCollaborator.objects.create(
            goal=invitation.goal,
            user=request.user,
            role=invitation.role
        )

        messages.success(request, f'Bạn đã chấp nhận lời mời tham gia mục tiêu "{invitation.goal.title}"')
    elif action == 'decline':
        # Từ chối lời mời
        invitation.status = 'declined'
        invitation.save()

        messages.info(request, f'Bạn đã từ chối lời mời tham gia mục tiêu "{invitation.goal.title}"')

    return redirect('notifications:list')

@login_required
def reminder_settings(request):
    """Cài đặt nhắc nhở cho tất cả các mục tiêu"""
    # Lấy cài đặt nhắc nhở hiện tại của người dùng
    user_goals = LearningGoal.objects.filter(user=request.user)

    # Lấy cài đặt mặc định từ mục tiêu gần nhất
    initial_data = {
        'reminder_enabled': True,
        'reminder_frequency': 'daily',
        'reminder_days_before': 1,
        'reminder_time': timezone.now().time(),
        'reminder_email': True,
        'reminder_app': True,
        'apply_to_all': True
    }

    # Nếu người dùng đã có mục tiêu, lấy cài đặt từ mục tiêu gần nhất
    if user_goals.exists():
        latest_goal = user_goals.latest('created_at')
        initial_data.update({
            'reminder_enabled': latest_goal.reminder_enabled,
            'reminder_frequency': latest_goal.reminder_frequency,
            'reminder_days_before': latest_goal.reminder_days_before,
            'reminder_time': latest_goal.reminder_time,
            'reminder_email': latest_goal.reminder_email,
            'reminder_app': latest_goal.reminder_app
        })

    if request.method == 'POST':
        form = ReminderSettingsForm(request.POST)
        if form.is_valid():
            # Lấy dữ liệu từ form
            reminder_enabled = form.cleaned_data['reminder_enabled']
            reminder_frequency = form.cleaned_data['reminder_frequency']
            reminder_days_before = form.cleaned_data['reminder_days_before']
            reminder_time = form.cleaned_data['reminder_time']
            reminder_email = form.cleaned_data['reminder_email']
            reminder_app = form.cleaned_data['reminder_app']
            apply_to_all = form.cleaned_data['apply_to_all']

            # Cập nhật cài đặt cho tất cả mục tiêu hiện tại nếu được yêu cầu
            if apply_to_all:
                user_goals.update(
                    reminder_enabled=reminder_enabled,
                    reminder_frequency=reminder_frequency,
                    reminder_days_before=reminder_days_before,
                    reminder_time=reminder_time,
                    reminder_email=reminder_email,
                    reminder_app=reminder_app
                )
                messages.success(request, 'Cài đặt nhắc nhở đã được cập nhật cho tất cả mục tiêu!')
            else:
                messages.success(request, 'Cài đặt nhắc nhở đã được lưu làm mặc định cho các mục tiêu mới!')

            return redirect('learning_goals:goal_list')
    else:
        form = ReminderSettingsForm(initial=initial_data)

    context = {
        'form': form,
        'title': 'Cài Đặt Nhắc Nhở Mục Tiêu',
        'button_text': 'Lưu Cài Đặt',
        'goal_count': user_goals.count()
    }

    return render(request, 'learning_goals/reminder_settings.html', context)
