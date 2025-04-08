from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Avg, Q
import json
from datetime import timedelta

from .models import (
    CornellNote, FeynmanNote, MindMap, 
    Project, UserProject, ProjectTask, 
    InteractiveExercise, CompetitionMode, CompetitionParticipant
)
from .models_learning_goals import LearningGoal, DailyStudyLog
from content.models import Subject, Topic, Lesson

# API cho mục tiêu học tập
@login_required
def api_learning_goals(request):
    """API lấy danh sách mục tiêu học tập"""
    if request.method == 'GET':
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
        
        # Chuyển đổi dữ liệu
        goals_data = []
        for goal in goals:
            goals_data.append({
                'id': goal.id,
                'title': goal.title,
                'description': goal.description,
                'goal_type': goal.goal_type,
                'goal_type_display': goal.get_goal_type_display(),
                'goal_metric': goal.goal_metric,
                'goal_metric_display': goal.get_goal_metric_display(),
                'target_value': goal.target_value,
                'current_value': goal.current_value,
                'progress_percentage': goal.get_progress_percentage(),
                'start_date': goal.start_date.strftime('%Y-%m-%d'),
                'end_date': goal.end_date.strftime('%Y-%m-%d') if goal.end_date else None,
                'is_completed': goal.is_completed,
                'is_active': goal.is_active,
                'subject': goal.subject.name if goal.subject else None,
                'created_at': goal.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': goal.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        return JsonResponse({
            'status': 'success',
            'data': goals_data
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

@csrf_exempt
@login_required
def api_create_learning_goal(request):
    """API tạo mục tiêu học tập mới"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Kiểm tra dữ liệu
            required_fields = ['title', 'goal_type', 'goal_metric', 'target_value']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Missing required field: {field}'
                    }, status=400)
            
            # Lấy môn học nếu có
            subject = None
            if 'subject_id' in data and data['subject_id']:
                try:
                    subject = Subject.objects.get(id=data['subject_id'])
                except Subject.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Subject not found'
                    }, status=404)
            
            # Tạo mục tiêu mới
            goal = LearningGoal(
                user=request.user,
                title=data['title'],
                description=data.get('description', ''),
                goal_type=data['goal_type'],
                goal_metric=data['goal_metric'],
                target_value=data['target_value'],
                subject=subject
            )
            
            # Thiết lập ngày bắt đầu và kết thúc
            if 'start_date' in data and data['start_date']:
                goal.start_date = data['start_date']
            
            if 'end_date' in data and data['end_date']:
                goal.end_date = data['end_date']
            
            goal.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Learning goal created successfully',
                'data': {
                    'id': goal.id,
                    'title': goal.title
                }
            })
        
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON'
            }, status=400)
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

@csrf_exempt
@login_required
def api_update_learning_goal(request, goal_id):
    """API cập nhật mục tiêu học tập"""
    goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)
    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            # Cập nhật thông tin
            if 'title' in data:
                goal.title = data['title']
            
            if 'description' in data:
                goal.description = data['description']
            
            if 'goal_type' in data:
                goal.goal_type = data['goal_type']
            
            if 'goal_metric' in data:
                goal.goal_metric = data['goal_metric']
            
            if 'target_value' in data:
                goal.target_value = data['target_value']
            
            if 'current_value' in data:
                goal.current_value = data['current_value']
            
            if 'start_date' in data:
                goal.start_date = data['start_date']
            
            if 'end_date' in data:
                goal.end_date = data['end_date']
            
            if 'is_completed' in data:
                goal.is_completed = data['is_completed']
            
            if 'is_active' in data:
                goal.is_active = data['is_active']
            
            if 'subject_id' in data:
                if data['subject_id']:
                    try:
                        goal.subject = Subject.objects.get(id=data['subject_id'])
                    except Subject.DoesNotExist:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Subject not found'
                        }, status=404)
                else:
                    goal.subject = None
            
            goal.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Learning goal updated successfully'
            })
        
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON'
            }, status=400)
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

@csrf_exempt
@login_required
def api_delete_learning_goal(request, goal_id):
    """API xóa mục tiêu học tập"""
    goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)
    
    if request.method == 'DELETE':
        goal.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Learning goal deleted successfully'
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

# API cho nhật ký học tập
@login_required
def api_daily_study_logs(request):
    """API lấy danh sách nhật ký học tập"""
    if request.method == 'GET':
        # Lấy khoảng thời gian
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Lấy danh sách nhật ký
        logs = DailyStudyLog.objects.filter(user=request.user, date__gte=start_date.date()).order_by('-date')
        
        # Chuyển đổi dữ liệu
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log.id,
                'date': log.date.strftime('%Y-%m-%d'),
                'total_minutes': log.total_minutes,
                'pomodoro_count': log.pomodoro_count,
                'notes_created': log.notes_created,
                'exercises_completed': log.exercises_completed,
                'competitions_participated': log.competitions_participated,
                'competition_points': log.competition_points,
                'subjects_studied': log.subjects_studied,
                'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': log.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        return JsonResponse({
            'status': 'success',
            'data': logs_data
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

@csrf_exempt
@login_required
def api_add_study_time(request):
    """API thêm thời gian học tập"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Kiểm tra dữ liệu
            if 'minutes' not in data or not isinstance(data['minutes'], int) or data['minutes'] <= 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid minutes value'
                }, status=400)
            
            # Lấy ngày
            date = timezone.now().date()
            if 'date' in data and data['date']:
                try:
                    date = timezone.datetime.strptime(data['date'], '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid date format'
                    }, status=400)
            
            # Lấy môn học
            subject = None
            if 'subject_id' in data and data['subject_id']:
                try:
                    subject = Subject.objects.get(id=data['subject_id'])
                except Subject.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Subject not found'
                    }, status=404)
            
            # Lấy hoặc tạo nhật ký học tập
            log, created = DailyStudyLog.objects.get_or_create(user=request.user, date=date)
            
            # Thêm thời gian học tập
            log.add_study_time(data['minutes'], subject)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Study time added successfully',
                'data': {
                    'id': log.id,
                    'date': log.date.strftime('%Y-%m-%d'),
                    'total_minutes': log.total_minutes
                }
            })
        
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON'
            }, status=400)
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

# API cho thống kê học tập
@login_required
def api_learning_statistics(request):
    """API lấy thống kê học tập"""
    if request.method == 'GET':
        # Lấy khoảng thời gian
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Lấy dữ liệu thống kê
        logs = DailyStudyLog.objects.filter(user=request.user, date__gte=start_date.date())
        
        # Tổng thời gian học tập
        total_minutes = logs.aggregate(total=Sum('total_minutes'))['total'] or 0
        
        # Thời gian học tập trung bình mỗi ngày
        avg_minutes = logs.aggregate(avg=Avg('total_minutes'))['avg'] or 0
        
        # Số ngày đã học
        study_days = logs.count()
        
        # Tổng số pomodoro
        total_pomodoros = logs.aggregate(total=Sum('pomodoro_count'))['total'] or 0
        
        # Tổng số ghi chú
        total_notes = logs.aggregate(total=Sum('notes_created'))['total'] or 0
        
        # Tổng số bài tập
        total_exercises = logs.aggregate(total=Sum('exercises_completed'))['total'] or 0
        
        # Tổng số cuộc thi
        total_competitions = logs.aggregate(total=Sum('competitions_participated'))['total'] or 0
        
        # Tổng điểm thi đấu
        total_competition_points = logs.aggregate(total=Sum('competition_points'))['total'] or 0
        
        # Thống kê theo môn học
        subjects_data = {}
        for log in logs:
            for subject_id, minutes in log.subjects_studied.items():
                if subject_id not in subjects_data:
                    subjects_data[subject_id] = 0
                subjects_data[subject_id] += minutes
        
        # Lấy thông tin chi tiết về môn học
        subjects_details = []
        for subject_id, minutes in subjects_data.items():
            try:
                subject = Subject.objects.get(id=subject_id)
                subjects_details.append({
                    'id': subject.id,
                    'name': subject.name,
                    'minutes': minutes,
                    'percentage': int((minutes / total_minutes) * 100) if total_minutes > 0 else 0
                })
            except Subject.DoesNotExist:
                continue
        
        # Sắp xếp theo thời gian học tập
        subjects_details.sort(key=lambda x: x['minutes'], reverse=True)
        
        # Thống kê mục tiêu học tập
        total_goals = LearningGoal.objects.filter(user=request.user).count()
        completed_goals = LearningGoal.objects.filter(user=request.user, is_completed=True).count()
        active_goals = LearningGoal.objects.filter(user=request.user, is_active=True, is_completed=False).count()
        
        # Tỷ lệ hoàn thành mục tiêu
        completion_rate = int((completed_goals / total_goals) * 100) if total_goals > 0 else 0
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'total_minutes': total_minutes,
                'avg_minutes': round(avg_minutes, 2),
                'study_days': study_days,
                'total_pomodoros': total_pomodoros,
                'total_notes': total_notes,
                'total_exercises': total_exercises,
                'total_competitions': total_competitions,
                'total_competition_points': total_competition_points,
                'subjects': subjects_details,
                'goals': {
                    'total': total_goals,
                    'completed': completed_goals,
                    'active': active_goals,
                    'completion_rate': completion_rate
                }
            }
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

# API cho tích hợp các tính năng học tập
@login_required
def api_learning_features(request):
    """API lấy danh sách các tính năng học tập"""
    if request.method == 'GET':
        # Lấy dữ liệu các tính năng học tập
        cornell_notes_count = CornellNote.objects.filter(user=request.user).count()
        feynman_notes_count = FeynmanNote.objects.filter(user=request.user).count()
        mind_maps_count = MindMap.objects.filter(user=request.user).count()
        projects_count = UserProject.objects.filter(user=request.user).count()
        exercises_count = InteractiveExercise.objects.filter(creator=request.user).count()
        competitions_count = CompetitionMode.objects.filter(creator=request.user).count()
        
        # Lấy số lượng tham gia
        participated_competitions = CompetitionParticipant.objects.filter(user=request.user).count()
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'cornell_notes': cornell_notes_count,
                'feynman_notes': feynman_notes_count,
                'mind_maps': mind_maps_count,
                'projects': projects_count,
                'exercises': exercises_count,
                'competitions': {
                    'created': competitions_count,
                    'participated': participated_competitions
                }
            }
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)
