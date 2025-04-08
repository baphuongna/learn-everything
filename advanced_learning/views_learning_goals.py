from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from datetime import timedelta

from .models_learning_goals import LearningGoal, DailyStudyLog
from .forms import LearningGoalForm
from content.models import Subject

@login_required
def learning_goals(request):
    """Danh sách mục tiêu học tập"""
    # Lọc theo trạng thái
    status = request.GET.get('status', 'active')
    
    # Lấy danh sách mục tiêu
    if status == 'completed':
        goals = LearningGoal.objects.filter(user=request.user, is_completed=True)
    elif status == 'all':
        goals = LearningGoal.objects.filter(user=request.user)
    else:  # active
        goals = LearningGoal.objects.filter(user=request.user, is_active=True, is_completed=False)
    
    # Sắp xếp
    goals = goals.order_by('-created_at')
    
    # Thống kê
    total_goals = LearningGoal.objects.filter(user=request.user).count()
    completed_goals = LearningGoal.objects.filter(user=request.user, is_completed=True).count()
    active_goals = LearningGoal.objects.filter(user=request.user, is_active=True, is_completed=False).count()
    
    # Tỷ lệ hoàn thành
    completion_rate = 0
    if total_goals > 0:
        completion_rate = int((completed_goals / total_goals) * 100)
    
    context = {
        'goals': goals,
        'status': status,
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'active_goals': active_goals,
        'completion_rate': completion_rate,
    }
    
    return render(request, 'advanced_learning/learning_goals/list.html', context)

@login_required
def create_learning_goal(request):
    """Tạo mục tiêu học tập mới"""
    if request.method == 'POST':
        form = LearningGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            
            messages.success(request, 'Mục tiêu học tập đã được tạo thành công!')
            return redirect('advanced_learning:learning_goals')
    else:
        form = LearningGoalForm()
    
    # Lấy danh sách môn học
    subjects = Subject.objects.all()
    
    context = {
        'form': form,
        'subjects': subjects,
        'is_create': True,
    }
    
    return render(request, 'advanced_learning/learning_goals/form.html', context)

@login_required
def edit_learning_goal(request, goal_id):
    """Chỉnh sửa mục tiêu học tập"""
    goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        form = LearningGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mục tiêu học tập đã được cập nhật thành công!')
            return redirect('advanced_learning:learning_goals')
    else:
        form = LearningGoalForm(instance=goal)
    
    # Lấy danh sách môn học
    subjects = Subject.objects.all()
    
    context = {
        'form': form,
        'goal': goal,
        'subjects': subjects,
        'is_create': False,
    }
    
    return render(request, 'advanced_learning/learning_goals/form.html', context)

@login_required
def delete_learning_goal(request, goal_id):
    """Xóa mục tiêu học tập"""
    goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Mục tiêu học tập đã được xóa thành công!')
        return redirect('advanced_learning:learning_goals')
    
    context = {
        'goal': goal,
    }
    
    return render(request, 'advanced_learning/learning_goals/confirm_delete.html', context)

@login_required
def complete_learning_goal(request, goal_id):
    """Đánh dấu mục tiêu học tập là đã hoàn thành"""
    goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        goal.is_completed = True
        goal.save(update_fields=['is_completed', 'updated_at'])
        messages.success(request, 'Mục tiêu học tập đã được đánh dấu là hoàn thành!')
        return redirect('advanced_learning:learning_goals')
    
    context = {
        'goal': goal,
    }
    
    return render(request, 'advanced_learning/learning_goals/confirm_complete.html', context)

@login_required
def reactivate_learning_goal(request, goal_id):
    """Kích hoạt lại mục tiêu học tập"""
    goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        goal.is_completed = False
        goal.is_active = True
        goal.save(update_fields=['is_completed', 'is_active', 'updated_at'])
        messages.success(request, 'Mục tiêu học tập đã được kích hoạt lại!')
        return redirect('advanced_learning:learning_goals')
    
    context = {
        'goal': goal,
    }
    
    return render(request, 'advanced_learning/learning_goals/confirm_reactivate.html', context)

@login_required
def daily_study_log(request):
    """Xem nhật ký học tập hàng ngày"""
    # Lấy nhật ký học tập trong 30 ngày qua
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    logs = DailyStudyLog.objects.filter(user=request.user, date__gte=last_30_days.date()).order_by('-date')
    
    # Tính tổng thời gian học tập
    total_minutes = logs.aggregate(total=Sum('total_minutes'))['total'] or 0
    
    # Tính thời gian học tập trung bình mỗi ngày
    avg_minutes = logs.aggregate(avg=Avg('total_minutes'))['avg'] or 0
    
    # Lấy nhật ký hôm nay
    today_log = DailyStudyLog.get_or_create_today(request.user)
    
    # Lấy danh sách môn học đã học
    subjects_studied = {}
    for log in logs:
        for subject_id, minutes in log.subjects_studied.items():
            subjects_studied[subject_id] = subjects_studied.get(subject_id, 0) + minutes
    
    # Sắp xếp môn học theo thời gian học tập
    subjects_studied = sorted(subjects_studied.items(), key=lambda x: x[1], reverse=True)
    
    # Lấy thông tin chi tiết về môn học
    subjects_details = []
    for subject_id, minutes in subjects_studied:
        try:
            subject = Subject.objects.get(id=subject_id)
            subjects_details.append({
                'subject': subject,
                'minutes': minutes,
                'percentage': int((minutes / total_minutes) * 100) if total_minutes > 0 else 0
            })
        except Subject.DoesNotExist:
            continue
    
    context = {
        'logs': logs,
        'today_log': today_log,
        'total_minutes': total_minutes,
        'avg_minutes': avg_minutes,
        'subjects_details': subjects_details,
    }
    
    return render(request, 'advanced_learning/learning_goals/daily_log.html', context)

@login_required
def add_study_time(request):
    """Thêm thời gian học tập thủ công"""
    if request.method == 'POST':
        minutes = int(request.POST.get('minutes', 0))
        subject_id = request.POST.get('subject')
        date_str = request.POST.get('date')
        
        if minutes <= 0:
            messages.error(request, 'Vui lòng nhập thời gian học tập hợp lệ!')
            return redirect('advanced_learning:daily_study_log')
        
        # Lấy ngày
        if date_str:
            try:
                date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                date = timezone.now().date()
        else:
            date = timezone.now().date()
        
        # Lấy môn học
        subject = None
        if subject_id:
            try:
                subject = Subject.objects.get(id=subject_id)
            except Subject.DoesNotExist:
                pass
        
        # Lấy hoặc tạo nhật ký học tập
        log, created = DailyStudyLog.objects.get_or_create(user=request.user, date=date)
        
        # Thêm thời gian học tập
        log.add_study_time(minutes, subject)
        
        messages.success(request, f'Đã thêm {minutes} phút học tập vào ngày {date.strftime("%d/%m/%Y")}!')
        return redirect('advanced_learning:daily_study_log')
    
    # Lấy danh sách môn học
    subjects = Subject.objects.all()
    
    context = {
        'subjects': subjects,
    }
    
    return render(request, 'advanced_learning/learning_goals/add_study_time.html', context)
