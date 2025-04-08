from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate

from .models import LearningGoal, GoalProgress

@login_required
def goal_progress_data(request, goal_id):
    """API endpoint để lấy dữ liệu tiến độ của mục tiêu theo thời gian"""
    try:
        # Lấy mục tiêu
        goal = LearningGoal.objects.get(id=goal_id, user=request.user)
        
        # Lấy lịch sử tiến độ
        progress_history = goal.progress_records.all().order_by('date')
        
        # Chuẩn bị dữ liệu cho biểu đồ
        labels = []
        progress_data = []
        expected_data = []
        
        # Nếu không có lịch sử tiến độ, trả về dữ liệu trống
        if not progress_history:
            return JsonResponse({
                'labels': [],
                'datasets': [
                    {
                        'label': 'Tiến độ thực tế',
                        'data': [],
                        'borderColor': 'rgba(75, 192, 192, 1)',
                        'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    },
                    {
                        'label': 'Tiến độ dự kiến',
                        'data': [],
                        'borderColor': 'rgba(153, 102, 255, 1)',
                        'backgroundColor': 'rgba(153, 102, 255, 0.2)',
                        'borderDash': [5, 5],
                    }
                ]
            })
        
        # Lấy ngày bắt đầu và kết thúc
        start_date = goal.start_date
        end_date = goal.end_date
        
        # Tính toán tiến độ dự kiến
        total_days = (end_date - start_date).days + 1
        
        # Tạo từ điển để lưu trữ giá trị tiến độ theo ngày
        progress_by_date = {}
        for record in progress_history:
            progress_by_date[record.date] = record.value
        
        # Tạo dữ liệu cho biểu đồ
        current_date = start_date
        last_progress = 0
        
        while current_date <= end_date:
            # Thêm ngày vào labels
            labels.append(current_date.strftime('%Y-%m-%d'))
            
            # Lấy tiến độ thực tế
            if current_date in progress_by_date:
                last_progress = progress_by_date[current_date]
            progress_data.append(last_progress)
            
            # Tính tiến độ dự kiến
            days_passed = (current_date - start_date).days + 1
            expected_progress = min(goal.target_value * days_passed / total_days, goal.target_value)
            expected_data.append(round(expected_progress, 2))
            
            # Tăng ngày
            current_date += timezone.timedelta(days=1)
        
        # Trả về dữ liệu cho biểu đồ
        return JsonResponse({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Tiến độ thực tế',
                    'data': progress_data,
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                },
                {
                    'label': 'Tiến độ dự kiến',
                    'data': expected_data,
                    'borderColor': 'rgba(153, 102, 255, 1)',
                    'backgroundColor': 'rgba(153, 102, 255, 0.2)',
                    'borderDash': [5, 5],
                }
            ]
        })
    except LearningGoal.DoesNotExist:
        return JsonResponse({'error': 'Mục tiêu không tồn tại'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def goal_completion_stats(request):
    """API endpoint để lấy thống kê hoàn thành mục tiêu theo thời gian"""
    try:
        # Lấy tham số từ request
        period = request.GET.get('period', 'month')  # day, week, month, year
        goal_type = request.GET.get('type', '')  # daily, weekly, monthly
        
        # Lấy mục tiêu đã hoàn thành
        completed_goals = LearningGoal.objects.filter(
            user=request.user,
            status='completed'
        )
        
        # Lọc theo loại mục tiêu
        if goal_type:
            completed_goals = completed_goals.filter(goal_type=goal_type)
        
        # Nhóm theo thời gian
        if period == 'day':
            # Nhóm theo ngày
            stats = completed_goals.annotate(
                date=TruncDate('updated_at')
            ).values('date').annotate(
                count=Count('id')
            ).order_by('date')
            
            # Chuẩn bị dữ liệu cho biểu đồ
            labels = [item['date'].strftime('%Y-%m-%d') for item in stats]
            data = [item['count'] for item in stats]
        elif period == 'week':
            # Nhóm theo tuần
            stats = completed_goals.annotate(
                week=TruncDate('updated_at', 'week')
            ).values('week').annotate(
                count=Count('id')
            ).order_by('week')
            
            # Chuẩn bị dữ liệu cho biểu đồ
            labels = [f"Tuần {item['week'].strftime('%U')} ({item['week'].strftime('%Y')})" for item in stats]
            data = [item['count'] for item in stats]
        elif period == 'month':
            # Nhóm theo tháng
            stats = completed_goals.annotate(
                month=TruncDate('updated_at', 'month')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')
            
            # Chuẩn bị dữ liệu cho biểu đồ
            labels = [item['month'].strftime('%m/%Y') for item in stats]
            data = [item['count'] for item in stats]
        else:  # year
            # Nhóm theo năm
            stats = completed_goals.annotate(
                year=TruncDate('updated_at', 'year')
            ).values('year').annotate(
                count=Count('id')
            ).order_by('year')
            
            # Chuẩn bị dữ liệu cho biểu đồ
            labels = [item['year'].strftime('%Y') for item in stats]
            data = [item['count'] for item in stats]
        
        # Trả về dữ liệu cho biểu đồ
        return JsonResponse({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Mục tiêu hoàn thành',
                    'data': data,
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                }
            ]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def goal_category_stats(request):
    """API endpoint để lấy thống kê mục tiêu theo danh mục"""
    try:
        # Lấy tất cả mục tiêu của người dùng
        goals = LearningGoal.objects.filter(user=request.user)
        
        # Nhóm theo danh mục và trạng thái
        stats = {}
        for category, category_name in LearningGoal.GOAL_CATEGORIES:
            category_goals = goals.filter(category=category)
            completed = category_goals.filter(status='completed').count()
            in_progress = category_goals.filter(status__in=['not_started', 'in_progress']).count()
            overdue = category_goals.filter(status='overdue').count()
            
            stats[category] = {
                'name': category_name,
                'completed': completed,
                'in_progress': in_progress,
                'overdue': overdue,
                'total': completed + in_progress + overdue
            }
        
        # Chuẩn bị dữ liệu cho biểu đồ
        categories = []
        completed_data = []
        in_progress_data = []
        overdue_data = []
        
        for category, data in stats.items():
            if data['total'] > 0:  # Chỉ hiển thị danh mục có mục tiêu
                categories.append(data['name'])
                completed_data.append(data['completed'])
                in_progress_data.append(data['in_progress'])
                overdue_data.append(data['overdue'])
        
        # Trả về dữ liệu cho biểu đồ
        return JsonResponse({
            'labels': categories,
            'datasets': [
                {
                    'label': 'Hoàn thành',
                    'data': completed_data,
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Đang thực hiện',
                    'data': in_progress_data,
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Quá hạn',
                    'data': overdue_data,
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                }
            ]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def goal_streak_data(request):
    """API endpoint để lấy dữ liệu chuỗi ngày hoàn thành mục tiêu liên tiếp"""
    try:
        # Lấy mục tiêu đã hoàn thành
        completed_goals = LearningGoal.objects.filter(
            user=request.user,
            status='completed'
        ).order_by('updated_at')
        
        # Nếu không có mục tiêu hoàn thành, trả về dữ liệu trống
        if not completed_goals:
            return JsonResponse({
                'current_streak': 0,
                'longest_streak': 0,
                'streak_data': []
            })
        
        # Tạo từ điển để lưu trữ ngày hoàn thành mục tiêu
        completion_dates = {}
        for goal in completed_goals:
            date_str = goal.updated_at.date().strftime('%Y-%m-%d')
            if date_str in completion_dates:
                completion_dates[date_str] += 1
            else:
                completion_dates[date_str] = 1
        
        # Tính toán chuỗi ngày liên tiếp
        dates = sorted(completion_dates.keys())
        current_streak = 1
        longest_streak = 1
        streak_start = dates[0]
        longest_streak_start = dates[0]
        longest_streak_end = dates[0]
        
        for i in range(1, len(dates)):
            prev_date = timezone.datetime.strptime(dates[i-1], '%Y-%m-%d').date()
            curr_date = timezone.datetime.strptime(dates[i], '%Y-%m-%d').date()
            
            # Kiểm tra xem hai ngày có liên tiếp không
            if (curr_date - prev_date).days == 1:
                current_streak += 1
                if current_streak > longest_streak:
                    longest_streak = current_streak
                    longest_streak_start = streak_start
                    longest_streak_end = dates[i]
            else:
                current_streak = 1
                streak_start = dates[i]
        
        # Tạo dữ liệu cho biểu đồ
        streak_data = []
        for date_str, count in completion_dates.items():
            streak_data.append({
                'date': date_str,
                'count': count
            })
        
        # Trả về dữ liệu
        return JsonResponse({
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'longest_streak_start': longest_streak_start,
            'longest_streak_end': longest_streak_end,
            'streak_data': streak_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
