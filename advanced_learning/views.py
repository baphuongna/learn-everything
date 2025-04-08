from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Sum, F, ExpressionWrapper, fields, Avg
from django.forms import inlineformset_factory
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from datetime import timedelta
from .models import PomodoroSession, CornellNote, MindMap, FeynmanNote, Project, ProjectTask, UserProject, InteractiveExercise, CompetitionMode, CompetitionQuestion, CompetitionAnswer, CompetitionParticipant, Notification
from .forms import CornellNoteForm, MindMapForm, FeynmanNoteForm, ProjectForm, ProjectTaskForm, UserProjectForm, InteractiveExerciseForm, CompetitionForm, CompetitionQuestionForm, CompetitionAnswerForm, CompetitionParticipantForm
from content.models import Subject, Topic, Lesson

# Pomodoro Timer Views
@login_required
def pomodoro_timer(request):
    """Hiển thị trang Pomodoro Timer"""
    subjects = Subject.objects.all()
    topics = Topic.objects.none()  # Sẽ được cập nhật bằng AJAX khi chọn subject

    # Lấy phiên Pomodoro đang hoạt động nếu có
    active_session = PomodoroSession.objects.filter(
        user=request.user,
        end_time__isnull=True
    ).first()

    context = {
        'subjects': subjects,
        'topics': topics,
        'active_session': active_session,
        'work_duration': 25,  # Mặc định 25 phút
        'break_duration': 5,  # Mặc định 5 phút
    }

    return render(request, 'advanced_learning/pomodoro/timer.html', context)

@login_required
@require_POST
def pomodoro_start(request):
    """Bắt đầu một phiên Pomodoro mới"""
    # Kiểm tra xem có phiên đang hoạt động không
    active_session = PomodoroSession.objects.filter(
        user=request.user,
        end_time__isnull=True
    ).first()

    if active_session:
        # Nếu có phiên đang hoạt động, kết thúc phiên đó trước
        active_session.end_time = timezone.now()
        active_session.save()
        messages.warning(request, 'Phiên Pomodoro trước đó đã được kết thúc tự động.')

    # Lấy thông tin từ form
    subject_id = request.POST.get('subject')
    topic_id = request.POST.get('topic')
    work_duration = int(request.POST.get('work_duration', 25))
    break_duration = int(request.POST.get('break_duration', 5))
    notes = request.POST.get('notes', '')

    # Tạo phiên mới
    session = PomodoroSession(
        user=request.user,
        start_time=timezone.now(),
        work_duration=work_duration,
        break_duration=break_duration,
        notes=notes
    )

    # Thêm subject và topic nếu có
    if subject_id:
        session.subject_id = subject_id
    if topic_id:
        session.topic_id = topic_id

    session.save()

    # Trả về JSON response cho AJAX
    return JsonResponse({
        'success': True,
        'session_id': session.id,
        'start_time': session.start_time.isoformat(),
        'work_duration': session.work_duration,
        'break_duration': session.break_duration
    })

@login_required
@require_POST
def pomodoro_end(request):
    """Kết thúc phiên Pomodoro hiện tại"""
    session_id = request.POST.get('session_id')
    completed_pomodoros = int(request.POST.get('completed_pomodoros', 0))

    # Tìm phiên Pomodoro
    session = get_object_or_404(PomodoroSession, id=session_id, user=request.user)

    # Cập nhật thông tin
    session.end_time = timezone.now()
    session.completed_pomodoros = completed_pomodoros
    session.save()

    # Trả về JSON response cho AJAX
    return JsonResponse({
        'success': True,
        'session_id': session.id,
        'completed_pomodoros': session.completed_pomodoros,
        'total_time': (session.end_time - session.start_time).total_seconds() // 60  # Thời gian tính bằng phút
    })

@login_required
def pomodoro_history(request):
    """Hiển thị lịch sử các phiên Pomodoro"""
    # Lấy tất cả các phiên Pomodoro của người dùng, sắp xếp theo thời gian bắt đầu giảm dần
    sessions = PomodoroSession.objects.filter(user=request.user).order_by('-start_time')

    # Tính tổng thời gian học tập
    total_minutes = 0
    total_pomodoros = 0

    for session in sessions:
        if session.end_time:  # Chỉ tính các phiên đã kết thúc
            duration = (session.end_time - session.start_time).total_seconds() // 60  # Thời gian tính bằng phút
            total_minutes += duration
            total_pomodoros += session.completed_pomodoros

    context = {
        'sessions': sessions,
        'total_minutes': total_minutes,
        'total_hours': total_minutes // 60,
        'remaining_minutes': total_minutes % 60,
        'total_pomodoros': total_pomodoros
    }

    return render(request, 'advanced_learning/pomodoro/history.html', context)

# Hệ thống ghi chú Cornell Views
@login_required
def cornell_note_list(request):
    """Hiển thị danh sách ghi chú Cornell của người dùng"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')

    notes = CornellNote.objects.filter(user=request.user).order_by('-created_at')

    # Áp dụng bộ lọc
    if search_query:
        notes = notes.filter(
            Q(title__icontains=search_query) |
            Q(main_notes__icontains=search_query) |
            Q(cue_column__icontains=search_query) |
            Q(summary__icontains=search_query)
        )

    if subject_id:
        notes = notes.filter(subject_id=subject_id)

    # Lấy danh sách các chủ đề cho bộ lọc
    subjects = Subject.objects.all()

    context = {
        'notes': notes,
        'subjects': subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
    }

    return render(request, 'advanced_learning/cornell_notes/list.html', context)

@login_required
def cornell_note_create(request):
    """Tạo ghi chú Cornell mới"""
    if request.method == 'POST':
        form = CornellNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, 'Ghi chú Cornell đã được tạo thành công!')
            return redirect('advanced_learning:cornell_note_detail', note_id=note.id)
    else:
        form = CornellNoteForm()

    context = {
        'form': form,
        'title': 'Tạo Ghi Chú Cornell Mới',
        'button_text': 'Tạo Ghi Chú',
    }

    return render(request, 'advanced_learning/cornell_notes/form.html', context)

@login_required
def cornell_note_detail(request, note_id):
    """Chi tiết ghi chú Cornell"""
    note = get_object_or_404(CornellNote, id=note_id, user=request.user)

    context = {
        'note': note,
    }

    return render(request, 'advanced_learning/cornell_notes/detail.html', context)

@login_required
def cornell_note_edit(request, note_id):
    """Chỉnh sửa ghi chú Cornell"""
    note = get_object_or_404(CornellNote, id=note_id, user=request.user)

    if request.method == 'POST':
        form = CornellNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ghi chú Cornell đã được cập nhật thành công!')
            return redirect('advanced_learning:cornell_note_detail', note_id=note.id)
    else:
        form = CornellNoteForm(instance=note)

    context = {
        'form': form,
        'note': note,
        'title': 'Chỉnh Sửa Ghi Chú Cornell',
        'button_text': 'Cập Nhật Ghi Chú',
    }

    return render(request, 'advanced_learning/cornell_notes/form.html', context)

@login_required
def cornell_note_delete(request, note_id):
    """Xóa ghi chú Cornell"""
    note = get_object_or_404(CornellNote, id=note_id, user=request.user)

    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Ghi chú Cornell đã được xóa thành công!')
        return redirect('advanced_learning:cornell_note_list')

    context = {
        'note': note,
    }

    return render(request, 'advanced_learning/cornell_notes/delete.html', context)

# Hệ thống Mind Mapping Views
@login_required
def mind_map_list(request):
    """Hiển thị danh sách sơ đồ tư duy của người dùng"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')

    mind_maps = MindMap.objects.filter(user=request.user).order_by('-created_at')

    # Áp dụng bộ lọc
    if search_query:
        mind_maps = mind_maps.filter(
            Q(title__icontains=search_query) |
            Q(central_topic__icontains=search_query)
        )

    if subject_id:
        mind_maps = mind_maps.filter(subject_id=subject_id)

    # Lấy danh sách các chủ đề cho bộ lọc
    subjects = Subject.objects.all()

    context = {
        'mind_maps': mind_maps,
        'subjects': subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
    }

    return render(request, 'advanced_learning/mind_maps/list.html', context)

@login_required
def mind_map_create(request):
    """Tạo sơ đồ tư duy mới"""
    if request.method == 'POST':
        form = MindMapForm(request.POST)
        if form.is_valid():
            mind_map = form.save(commit=False)
            mind_map.user = request.user
            mind_map.save()
            messages.success(request, 'Sơ đồ tư duy đã được tạo thành công!')
            return redirect('advanced_learning:mind_map_detail', map_id=mind_map.id)
    else:
        form = MindMapForm()

    context = {
        'form': form,
        'title': 'Tạo Sơ Đồ Tư Duy Mới',
        'button_text': 'Tạo Sơ Đồ',
    }

    return render(request, 'advanced_learning/mind_maps/form.html', context)

@login_required
def mind_map_detail(request, map_id):
    """Chi tiết sơ đồ tư duy"""
    mind_map = get_object_or_404(MindMap, id=map_id, user=request.user)

    context = {
        'mind_map': mind_map,
    }

    return render(request, 'advanced_learning/mind_maps/detail.html', context)

@login_required
def mind_map_edit(request, map_id):
    """Chỉnh sửa sơ đồ tư duy"""
    mind_map = get_object_or_404(MindMap, id=map_id, user=request.user)

    if request.method == 'POST':
        form = MindMapForm(request.POST, instance=mind_map)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sơ đồ tư duy đã được cập nhật thành công!')
            return redirect('advanced_learning:mind_map_detail', map_id=mind_map.id)
    else:
        form = MindMapForm(instance=mind_map)

    context = {
        'form': form,
        'mind_map': mind_map,
        'title': 'Chỉnh Sửa Sơ Đồ Tư Duy',
        'button_text': 'Cập Nhật Sơ Đồ',
    }

    return render(request, 'advanced_learning/mind_maps/form.html', context)

@login_required
def mind_map_delete(request, map_id):
    """Xóa sơ đồ tư duy"""
    mind_map = get_object_or_404(MindMap, id=map_id, user=request.user)

    if request.method == 'POST':
        mind_map.delete()
        messages.success(request, 'Sơ đồ tư duy đã được xóa thành công!')
        return redirect('advanced_learning:mind_map_list')

    context = {
        'mind_map': mind_map,
    }

    return render(request, 'advanced_learning/mind_maps/delete.html', context)

# Phương pháp Feynman Technique Views
@login_required
def feynman_note_list(request):
    """Hiển thị danh sách ghi chú Feynman của người dùng"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')

    notes = FeynmanNote.objects.filter(user=request.user).order_by('-created_at')

    # Áp dụng bộ lọc
    if search_query:
        notes = notes.filter(
            Q(title__icontains=search_query) |
            Q(concept__icontains=search_query) |
            Q(explanation__icontains=search_query) |
            Q(gaps_identified__icontains=search_query) |
            Q(refined_explanation__icontains=search_query)
        )

    if subject_id:
        notes = notes.filter(subject_id=subject_id)

    # Lấy danh sách các chủ đề cho bộ lọc
    subjects = Subject.objects.all()

    context = {
        'notes': notes,
        'subjects': subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
    }

    return render(request, 'advanced_learning/feynman_notes/list.html', context)

@login_required
def feynman_note_create(request):
    """Tạo ghi chú Feynman mới"""
    if request.method == 'POST':
        form = FeynmanNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, 'Ghi chú Feynman đã được tạo thành công!')
            return redirect('advanced_learning:feynman_note_detail', note_id=note.id)
    else:
        form = FeynmanNoteForm()

    context = {
        'form': form,
        'title': 'Tạo Ghi Chú Feynman Mới',
        'button_text': 'Tạo Ghi Chú',
    }

    return render(request, 'advanced_learning/feynman_notes/form.html', context)

@login_required
def feynman_note_detail(request, note_id):
    """Chi tiết ghi chú Feynman"""
    note = get_object_or_404(FeynmanNote, id=note_id, user=request.user)

    context = {
        'note': note,
    }

    return render(request, 'advanced_learning/feynman_notes/detail.html', context)

@login_required
def feynman_note_edit(request, note_id):
    """Chỉnh sửa ghi chú Feynman"""
    note = get_object_or_404(FeynmanNote, id=note_id, user=request.user)

    if request.method == 'POST':
        form = FeynmanNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ghi chú Feynman đã được cập nhật thành công!')
            return redirect('advanced_learning:feynman_note_detail', note_id=note.id)
    else:
        form = FeynmanNoteForm(instance=note)

    context = {
        'form': form,
        'note': note,
        'title': 'Chỉnh Sửa Ghi Chú Feynman',
        'button_text': 'Cập Nhật Ghi Chú',
    }

    return render(request, 'advanced_learning/feynman_notes/form.html', context)

@login_required
def feynman_note_delete(request, note_id):
    """Xóa ghi chú Feynman"""
    note = get_object_or_404(FeynmanNote, id=note_id, user=request.user)

    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Ghi chú Feynman đã được xóa thành công!')
        return redirect('advanced_learning:feynman_note_list')

    context = {
        'note': note,
    }

    return render(request, 'advanced_learning/feynman_notes/delete.html', context)

# Hệ thống học tập dựa trên dự án Views
@login_required
def project_list(request):
    """Hiển thị danh sách dự án học tập"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    difficulty = request.GET.get('difficulty', '')

    # Lấy danh sách dự án
    projects = Project.objects.all().order_by('title')

    # Lấy danh sách dự án của người dùng
    user_projects = UserProject.objects.filter(user=request.user)
    user_project_ids = user_projects.values_list('project_id', flat=True)

    # Áp dụng bộ lọc
    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if subject_id:
        projects = projects.filter(subject_id=subject_id)

    if difficulty:
        projects = projects.filter(difficulty_level=difficulty)

    # Lấy danh sách các chủ đề cho bộ lọc
    subjects = Subject.objects.all()

    # Thêm thông tin về số nhiệm vụ trong mỗi dự án
    projects = projects.annotate(task_count=Count('tasks'))

    context = {
        'projects': projects,
        'user_projects': user_projects,
        'user_project_ids': user_project_ids,
        'subjects': subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
        'selected_difficulty': difficulty,
        'difficulty_levels': Project.objects.values_list('difficulty_level', flat=True).distinct(),
    }

    return render(request, 'advanced_learning/projects/list.html', context)

@login_required
def project_detail(request, project_id):
    """Chi tiết dự án học tập"""
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all().order_by('order')

    # Kiểm tra xem người dùng đã tham gia dự án này chưa
    user_project = UserProject.objects.filter(user=request.user, project=project).first()

    context = {
        'project': project,
        'tasks': tasks,
        'user_project': user_project,
    }

    return render(request, 'advanced_learning/projects/detail.html', context)

@login_required
def create_mindmap_from_project(request, project_id):
    """Tạo Mind Map từ dự án học tập"""
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = MindMapForm(request.POST)
        if form.is_valid():
            mind_map = form.save(commit=False)
            mind_map.user = request.user
            mind_map.save()

            messages.success(request, 'Mind Map đã được tạo thành công!')
            return redirect('advanced_learning:mind_map_detail', mind_map_id=mind_map.id)
    else:
        # Điền trước thông tin từ dự án
        # Tạo danh sách các nút con từ các nhiệm vụ của dự án
        tasks = project.tasks.all()
        child_nodes = ''
        for task in tasks:
            child_nodes += f'{task.title}\n'

        initial_data = {
            'title': f'Mind Map về {project.title}',
            'central_topic': project.title,
            'child_nodes': child_nodes,
            'description': project.description,
        }

        # Nếu dự án có chủ đề, gán cho Mind Map
        if project.subject:
            initial_data['subject'] = project.subject.id

        form = MindMapForm(initial=initial_data)

    context = {
        'form': form,
        'project': project,
        'title': 'Tạo Mind Map từ Dự Án',
        'button_text': 'Tạo Mind Map',
    }

    return render(request, 'advanced_learning/mind_maps/form.html', context)

@login_required
def start_project(request, project_id):
    """Bắt đầu một dự án học tập"""
    project = get_object_or_404(Project, id=project_id)

    # Kiểm tra xem người dùng đã tham gia dự án này chưa
    user_project = UserProject.objects.filter(user=request.user, project=project).first()

    if user_project:
        messages.warning(request, 'Bạn đã tham gia dự án này rồi!')
        return redirect('advanced_learning:project_detail', project_id=project.id)

    if request.method == 'POST':
        form = UserProjectForm(request.POST)
        if form.is_valid():
            user_project = form.save(commit=False)
            user_project.user = request.user
            user_project.project = project
            user_project.status = 'in_progress'
            user_project.started_at = timezone.now()
            user_project.save()
            messages.success(request, 'Bạn đã bắt đầu dự án thành công!')
            return redirect('advanced_learning:project_detail', project_id=project.id)
    else:
        form = UserProjectForm(initial={'status': 'in_progress', 'progress': 0})

    context = {
        'project': project,
        'form': form,
    }

    return render(request, 'advanced_learning/projects/start_project.html', context)

@login_required
def update_project_progress(request, project_id):
    """Cập nhật tiến độ dự án"""
    project = get_object_or_404(Project, id=project_id)
    user_project = get_object_or_404(UserProject, user=request.user, project=project)

    if request.method == 'POST':
        form = UserProjectForm(request.POST, instance=user_project)
        if form.is_valid():
            user_project = form.save(commit=False)

            # Nếu trạng thái là hoàn thành và chưa có ngày hoàn thành
            if user_project.status == 'completed' and not user_project.completed_at:
                user_project.completed_at = timezone.now()
                user_project.progress = 100

            user_project.save()
            messages.success(request, 'Tiến độ dự án đã được cập nhật thành công!')
            return redirect('advanced_learning:project_detail', project_id=project.id)
    else:
        form = UserProjectForm(instance=user_project)

    context = {
        'project': project,
        'user_project': user_project,
        'form': form,
    }

    return render(request, 'advanced_learning/projects/update_progress.html', context)

@login_required
def my_projects(request):
    """Hiển thị danh sách dự án của người dùng"""
    status_filter = request.GET.get('status', '')

    # Lấy danh sách dự án của người dùng
    user_projects = UserProject.objects.filter(user=request.user).order_by('-started_at')

    # Đếm số dự án đã hoàn thành
    completed_projects = user_projects.filter(status='completed').count()

    # Tính tiến độ cao nhất
    highest_progress = user_projects.order_by('-progress').values_list('progress', flat=True).first() or 0

    # Áp dụng bộ lọc
    if status_filter:
        user_projects = user_projects.filter(status=status_filter)

    context = {
        'user_projects': user_projects,
        'selected_status': status_filter,
        'completed_projects': completed_projects,
        'highest_progress': highest_progress,
    }

    return render(request, 'advanced_learning/projects/my_projects.html', context)

# Bài tập thực hành tương tác Views
@login_required
def exercise_list(request):
    """Hiển thị danh sách bài tập thực hành tương tác"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    exercise_type = request.GET.get('type', '')

    # Lấy danh sách bài tập
    exercises = InteractiveExercise.objects.all().order_by('-created_at')

    # Áp dụng bộ lọc
    if search_query:
        exercises = exercises.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if subject_id:
        exercises = exercises.filter(lesson__topic__subject_id=subject_id)

    if exercise_type:
        exercises = exercises.filter(exercise_type=exercise_type)

    # Lấy danh sách các chủ đề cho bộ lọc
    subjects = Subject.objects.all()

    # Lấy danh sách các loại bài tập
    exercise_types = InteractiveExercise.EXERCISE_TYPES

    context = {
        'exercises': exercises,
        'subjects': subjects,
        'exercise_types': exercise_types,
        'search_query': search_query,
        'selected_subject': subject_id,
        'selected_type': exercise_type,
    }

    return render(request, 'advanced_learning/exercises/list.html', context)

@login_required
def exercise_detail(request, exercise_id):
    """Chi tiết bài tập thực hành tương tác"""
    exercise = get_object_or_404(InteractiveExercise, id=exercise_id)

    # Kiểm tra xem người dùng đã hoàn thành bài tập này chưa
    user_submission = None
    show_solution = False

    # Nếu người dùng đã hoàn thành bài tập, hiển thị giải pháp
    if user_submission and user_submission.is_correct:
        show_solution = True

    context = {
        'exercise': exercise,
        'user_submission': user_submission,
        'show_solution': show_solution,
    }

    return render(request, 'advanced_learning/exercises/detail.html', context)

@login_required
def create_cornell_from_exercise(request, exercise_id):
    """Tạo ghi chú Cornell từ bài tập thực hành tương tác"""
    exercise = get_object_or_404(InteractiveExercise, id=exercise_id)

    if request.method == 'POST':
        form = CornellNoteForm(request.POST)
        if form.is_valid():
            cornell_note = form.save(commit=False)
            cornell_note.user = request.user
            cornell_note.save()

            messages.success(request, 'Ghi chú Cornell đã được tạo thành công!')
            return redirect('advanced_learning:cornell_note_detail', note_id=cornell_note.id)
    else:
        # Điền trước thông tin từ bài tập
        initial_data = {
            'title': f'Ghi chú về {exercise.title}',
            'topic': exercise.lesson.topic.name if exercise.lesson and exercise.lesson.topic else '',
            'main_notes': exercise.description,
            'cues': f'Bài tập: {exercise.title}\nLoại: {exercise.get_exercise_type_display()}',
            'summary': f'Ghi chú từ bài tập thực hành "{exercise.title}"',
        }
        form = CornellNoteForm(initial=initial_data)

    context = {
        'form': form,
        'exercise': exercise,
        'title': 'Tạo Ghi Chú Cornell từ Bài Tập',
        'button_text': 'Tạo Ghi Chú',
    }

    return render(request, 'advanced_learning/cornell_notes/form.html', context)

@login_required
@require_POST
def submit_exercise(request, exercise_id):
    """Xử lý nộp bài tập"""
    exercise = get_object_or_404(InteractiveExercise, id=exercise_id)

    # Lấy dữ liệu từ form
    submission_data = request.POST.get('submission', '')

    # Xử lý kiểm tra đáp án tùy theo loại bài tập
    is_correct = False
    feedback = ''

    if exercise.exercise_type == 'code':
        # Đối với bài tập lập trình, có thể cần xử lý phức tạp hơn
        # Ở đây chỉ là một ví dụ đơn giản
        if submission_data.strip() == exercise.solution.strip():
            is_correct = True
            feedback = 'Chúc mừng! Bạn đã hoàn thành bài tập thành công.'
        else:
            feedback = 'Chưa đúng. Hãy thử lại.'

    elif exercise.exercise_type == 'quiz':
        # Đối với câu đố, kiểm tra đáp án
        if submission_data.strip().lower() == exercise.solution.strip().lower():
            is_correct = True
            feedback = 'Chúc mừng! Đáp án của bạn là chính xác.'
        else:
            feedback = 'Chưa đúng. Hãy thử lại.'

    else:
        # Xử lý các loại bài tập khác
        feedback = 'Cảm ơn bạn đã nộp bài tập.'

    # Lưu kết quả nộp bài
    # UserExerciseSubmission.objects.create(
    #     user=request.user,
    #     exercise=exercise,
    #     submission=submission_data,
    #     is_correct=is_correct
    # )

    # Trả về kết quả
    return JsonResponse({
        'success': True,
        'is_correct': is_correct,
        'feedback': feedback,
        'solution': exercise.solution if is_correct else None
    })

@login_required
def create_exercise(request):
    """Tạo bài tập thực hành tương tác mới"""
    if request.method == 'POST':
        form = InteractiveExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save()
            messages.success(request, 'Bài tập thực hành tương tác đã được tạo thành công!')
            return redirect('advanced_learning:exercise_detail', exercise_id=exercise.id)
    else:
        form = InteractiveExerciseForm()

    context = {
        'form': form,
        'title': 'Tạo Bài Tập Thực Hành Tương Tác Mới',
        'button_text': 'Tạo Bài Tập',
    }

    return render(request, 'advanced_learning/exercises/form.html', context)

@login_required
def edit_exercise(request, exercise_id):
    """Chỉnh sửa bài tập thực hành tương tác"""
    exercise = get_object_or_404(InteractiveExercise, id=exercise_id)

    if request.method == 'POST':
        form = InteractiveExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bài tập thực hành tương tác đã được cập nhật thành công!')
            return redirect('advanced_learning:exercise_detail', exercise_id=exercise.id)
    else:
        form = InteractiveExerciseForm(instance=exercise)

    context = {
        'form': form,
        'exercise': exercise,
        'title': 'Chỉnh Sửa Bài Tập Thực Hành Tương Tác',
        'button_text': 'Cập Nhật Bài Tập',
    }

    return render(request, 'advanced_learning/exercises/form.html', context)

@login_required
def delete_exercise(request, exercise_id):
    """Xóa bài tập thực hành tương tác"""
    exercise = get_object_or_404(InteractiveExercise, id=exercise_id)

    if request.method == 'POST':
        exercise.delete()
        messages.success(request, 'Bài tập thực hành tương tác đã được xóa thành công!')
        return redirect('advanced_learning:exercise_list')

    context = {
        'exercise': exercise,
    }

    return render(request, 'advanced_learning/exercises/delete.html', context)

# Chế độ thi đấu Views
@login_required
def competition_list(request):
    """Hiển thị danh sách các cuộc thi đấu"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    status = request.GET.get('status', '')

    # Lấy danh sách cuộc thi
    competitions = CompetitionMode.objects.all().order_by('-start_time')

    # Áp dụng bộ lọc
    if search_query:
        competitions = competitions.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if subject_id:
        competitions = competitions.filter(subject_id=subject_id)

    if status:
        now = timezone.now()
        if status == 'upcoming':
            competitions = competitions.filter(start_time__gt=now)
        elif status == 'active':
            competitions = competitions.filter(start_time__lte=now, end_time__gte=now, is_active=True)
        elif status == 'past':
            competitions = competitions.filter(end_time__lt=now)

    # Lấy danh sách các chủ đề cho bộ lọc
    subjects = Subject.objects.all()

    # Lấy danh sách các cuộc thi mà người dùng đã tham gia
    user_competitions = CompetitionParticipant.objects.filter(user=request.user).values_list('competition_id', flat=True)

    context = {
        'competitions': competitions,
        'subjects': subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
        'selected_status': status,
        'user_competitions': user_competitions,
    }

    return render(request, 'advanced_learning/competitions/list.html', context)

@login_required
def competition_detail(request, competition_id):
    """Chi tiết cuộc thi đấu"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)

    # Kiểm tra xem người dùng đã tham gia cuộc thi này chưa
    user_participation = CompetitionParticipant.objects.filter(user=request.user, competition=competition).first()

    # Kiểm tra xem cuộc thi có đang diễn ra không
    now = timezone.now()
    is_active = competition.is_active and competition.start_time <= now and competition.end_time >= now

    # Kiểm tra xem cuộc thi có đạt giới hạn số người tham gia không
    participant_count = CompetitionParticipant.objects.filter(competition=competition).count()
    can_join = competition.max_participants == 0 or participant_count < competition.max_participants

    # Lấy bảng xếp hạng
    leaderboard = CompetitionParticipant.objects.filter(competition=competition, score__gt=0).order_by('-score')[:10]

    context = {
        'competition': competition,
        'user_participation': user_participation,
        'is_active': is_active,
        'can_join': can_join,
        'participant_count': participant_count,
        'leaderboard': leaderboard,
    }

    return render(request, 'advanced_learning/competitions/detail.html', context)

@login_required
def join_competition(request, competition_id):
    """Tham gia cuộc thi đấu"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)

    # Kiểm tra xem người dùng đã tham gia cuộc thi này chưa
    user_participation = CompetitionParticipant.objects.filter(user=request.user, competition=competition).first()

    if user_participation:
        messages.warning(request, 'Bạn đã tham gia cuộc thi này rồi!')
        return redirect('advanced_learning:competition_detail', competition_id=competition.id)

    # Kiểm tra xem cuộc thi có đang diễn ra không
    now = timezone.now()
    if not (competition.is_active and competition.start_time <= now and competition.end_time >= now):
        messages.error(request, 'Cuộc thi này không còn hoạt động!')
        return redirect('advanced_learning:competition_detail', competition_id=competition.id)

    # Kiểm tra xem cuộc thi có đạt giới hạn số người tham gia không
    participant_count = CompetitionParticipant.objects.filter(competition=competition).count()
    if competition.max_participants > 0 and participant_count >= competition.max_participants:
        messages.error(request, 'Cuộc thi này đã đạt giới hạn số người tham gia!')
        return redirect('advanced_learning:competition_detail', competition_id=competition.id)

    if request.method == 'POST':
        # Tạo một bản ghi tham gia mới
        user_participation = CompetitionParticipant.objects.create(
            user=request.user,
            competition=competition,
            start_time=timezone.now(),
            score=0
        )

        messages.success(request, 'Bạn đã tham gia cuộc thi thành công!')
        return redirect('advanced_learning:take_competition', competition_id=competition.id)

    context = {
        'competition': competition,
    }

    return render(request, 'advanced_learning/competitions/join.html', context)

@login_required
def take_competition(request, competition_id):
    """Làm bài thi"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)

    # Kiểm tra xem người dùng đã tham gia cuộc thi này chưa
    user_participation = get_object_or_404(CompetitionParticipant, user=request.user, competition=competition)

    # Kiểm tra xem người dùng đã hoàn thành bài thi chưa
    if user_participation.end_time:
        messages.warning(request, 'Bạn đã hoàn thành bài thi này rồi!')
        return redirect('advanced_learning:competition_result', competition_id=competition.id)

    # Lấy danh sách câu hỏi
    questions = CompetitionQuestion.objects.filter(competition=competition).order_by('order')

    if request.method == 'POST':
        # Tính điểm
        score = 0
        for question in questions:
            answer_id = request.POST.get(f'question_{question.id}')
            if answer_id:
                answer = get_object_or_404(CompetitionAnswer, id=answer_id)
                if answer.is_correct:
                    score += question.points

        # Cập nhật kết quả
        user_participation.end_time = timezone.now()
        user_participation.score = score
        user_participation.save()

        # Cập nhật xếp hạng
        update_competition_rankings(competition)

        messages.success(request, 'Bạn đã hoàn thành bài thi thành công!')
        return redirect('advanced_learning:competition_result', competition_id=competition.id)

    # Tính thời gian còn lại
    time_elapsed = (timezone.now() - user_participation.start_time).total_seconds() // 60
    time_remaining = max(0, competition.time_limit - time_elapsed)

    context = {
        'competition': competition,
        'questions': questions,
        'time_remaining': time_remaining,
    }

    return render(request, 'advanced_learning/competitions/take.html', context)

@login_required
def competition_result(request, competition_id):
    """Kết quả thi đấu"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)

    # Kiểm tra xem người dùng đã tham gia cuộc thi này chưa
    user_participation = get_object_or_404(CompetitionParticipant, user=request.user, competition=competition)

    # Kiểm tra xem người dùng đã hoàn thành bài thi chưa
    if not user_participation.end_time:
        messages.warning(request, 'Bạn chưa hoàn thành bài thi này!')
        return redirect('advanced_learning:take_competition', competition_id=competition.id)

    # Lấy bảng xếp hạng
    leaderboard = CompetitionParticipant.objects.filter(competition=competition, score__gt=0).order_by('-score')[:10]

    # Tính tổng điểm có thể
    total_possible_score = CompetitionQuestion.objects.filter(competition=competition).aggregate(total=Sum('points'))['total'] or 0

    context = {
        'competition': competition,
        'user_participation': user_participation,
        'leaderboard': leaderboard,
        'total_possible_score': total_possible_score,
    }

    return render(request, 'advanced_learning/competitions/result.html', context)

@login_required
def create_feynman_from_competition(request, competition_id):
    """Tạo Feynman Note từ cuộc thi đấu"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)

    # Kiểm tra xem người dùng đã tham gia cuộc thi này chưa
    user_participation = get_object_or_404(CompetitionParticipant, user=request.user, competition=competition)

    # Kiểm tra xem người dùng đã hoàn thành bài thi chưa
    if not user_participation.end_time:
        messages.warning(request, 'Bạn chưa hoàn thành bài thi này!')
        return redirect('advanced_learning:take_competition', competition_id=competition.id)

    if request.method == 'POST':
        form = FeynmanNoteForm(request.POST)
        if form.is_valid():
            feynman_note = form.save(commit=False)
            feynman_note.user = request.user
            feynman_note.save()

            messages.success(request, 'Feynman Note đã được tạo thành công!')
            return redirect('advanced_learning:feynman_note_detail', note_id=feynman_note.id)
    else:
        # Lấy các câu hỏi trong cuộc thi
        questions = CompetitionQuestion.objects.filter(competition=competition).order_by('order')

        # Tạo nội dung cho Feynman Note
        concept = f'Kiến thức từ cuộc thi: {competition.title}'
        explanation = ''

        for question in questions:
            explanation += f'Câu hỏi: {question.question_text}\n'
            # Thêm các đáp án đúng
            correct_answers = CompetitionAnswer.objects.filter(question=question, is_correct=True)
            for answer in correct_answers:
                explanation += f'- Đáp án đúng: {answer.answer_text}\n'
            explanation += '\n'

        initial_data = {
            'title': f'Feynman Note về {competition.title}',
            'concept': concept,
            'explanation': explanation,
            'analogy': f'Cuộc thi {competition.title} kiểm tra kiến thức về {competition.subject.name if competition.subject else "chủ đề này"}.',
            'simplification': f'Điểm số của bạn: {user_participation.score}. Hãy giải thích lại các khái niệm trong cuộc thi này bằng ngôn ngữ đơn giản nhất.',
        }

        # Nếu cuộc thi có chủ đề, gán cho Feynman Note
        if competition.subject:
            initial_data['subject'] = competition.subject.id

        form = FeynmanNoteForm(initial=initial_data)

    context = {
        'form': form,
        'competition': competition,
        'title': 'Tạo Feynman Note từ Cuộc Thi',
        'button_text': 'Tạo Feynman Note',
    }

    return render(request, 'advanced_learning/feynman_notes/form.html', context)

@login_required
def my_competitions(request):
    """Danh sách các cuộc thi đã tham gia"""
    # Lấy danh sách các cuộc thi đã tham gia
    participations = CompetitionParticipant.objects.filter(user=request.user).order_by('-start_time')

    # Tính điểm cao nhất
    highest_score = participations.filter(end_time__isnull=False).order_by('-score').values_list('score', flat=True).first() or 0

    # Tím xếp hạng cao nhất (số nhỏ nhất)
    best_rank = participations.filter(rank__isnull=False).order_by('rank').values_list('rank', flat=True).first()

    context = {
        'participations': participations,
        'highest_score': highest_score,
        'best_rank': best_rank,
    }

    return render(request, 'advanced_learning/competitions/my_competitions.html', context)

@login_required
def create_competition(request):
    """Tạo cuộc thi mới"""
    if request.method == 'POST':
        form = CompetitionForm(request.POST)
        if form.is_valid():
            competition = form.save()
            messages.success(request, 'Cuộc thi đã được tạo thành công!')
            return redirect('advanced_learning:edit_competition_questions', competition_id=competition.id)
    else:
        form = CompetitionForm(initial={
            'start_time': timezone.now(),
            'end_time': timezone.now() + timezone.timedelta(days=7),
            'time_limit': 60,
            'max_participants': 0,
            'is_active': False,
        })

    context = {
        'form': form,
        'title': 'Tạo Cuộc Thi Mới',
        'button_text': 'Tiếp Theo',
    }

    return render(request, 'advanced_learning/competitions/form.html', context)

@login_required
def edit_competition(request, competition_id):
    """Chỉnh sửa cuộc thi"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)

    if request.method == 'POST':
        form = CompetitionForm(request.POST, instance=competition)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuộc thi đã được cập nhật thành công!')
            return redirect('advanced_learning:competition_detail', competition_id=competition.id)
    else:
        form = CompetitionForm(instance=competition)

    context = {
        'form': form,
        'competition': competition,
        'title': 'Chỉnh Sửa Cuộc Thi',
        'button_text': 'Cập Nhật',
    }

    return render(request, 'advanced_learning/competitions/form.html', context)

@login_required
def edit_competition_questions(request, competition_id):
    """Chỉnh sửa câu hỏi trong cuộc thi"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)
    questions = CompetitionQuestion.objects.filter(competition=competition).order_by('order')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_question':
            # Thêm câu hỏi mới
            form = CompetitionQuestionForm(request.POST)
            if form.is_valid():
                question = form.save(commit=False)
                question.competition = competition
                question.save()
                messages.success(request, 'Câu hỏi đã được thêm thành công!')
                return redirect('advanced_learning:edit_question_answers', competition_id=competition.id, question_id=question.id)

        elif action == 'delete_question':
            # Xóa câu hỏi
            question_id = request.POST.get('question_id')
            question = get_object_or_404(CompetitionQuestion, id=question_id, competition=competition)
            question.delete()
            messages.success(request, 'Câu hỏi đã được xóa thành công!')
            return redirect('advanced_learning:edit_competition_questions', competition_id=competition.id)

        elif action == 'finish':
            # Hoàn thành chỉnh sửa câu hỏi
            return redirect('advanced_learning:competition_detail', competition_id=competition.id)

    # Form cho câu hỏi mới
    form = CompetitionQuestionForm(initial={'order': questions.count(), 'points': 1})

    context = {
        'competition': competition,
        'questions': questions,
        'form': form,
    }

    return render(request, 'advanced_learning/competitions/edit_questions.html', context)

@login_required
def edit_question_answers(request, competition_id, question_id):
    """Chỉnh sửa đáp án cho câu hỏi"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)
    question = get_object_or_404(CompetitionQuestion, id=question_id, competition=competition)
    answers = CompetitionAnswer.objects.filter(question=question)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_answer':
            # Thêm đáp án mới
            form = CompetitionAnswerForm(request.POST)
            if form.is_valid():
                answer = form.save(commit=False)
                answer.question = question
                answer.save()
                messages.success(request, 'Đáp án đã được thêm thành công!')
                return redirect('advanced_learning:edit_question_answers', competition_id=competition.id, question_id=question.id)

        elif action == 'delete_answer':
            # Xóa đáp án
            answer_id = request.POST.get('answer_id')
            answer = get_object_or_404(CompetitionAnswer, id=answer_id, question=question)
            answer.delete()
            messages.success(request, 'Đáp án đã được xóa thành công!')
            return redirect('advanced_learning:edit_question_answers', competition_id=competition.id, question_id=question.id)

        elif action == 'finish':
            # Hoàn thành chỉnh sửa đáp án
            return redirect('advanced_learning:edit_competition_questions', competition_id=competition.id)

    # Form cho đáp án mới
    form = CompetitionAnswerForm()

    context = {
        'competition': competition,
        'question': question,
        'answers': answers,
        'form': form,
    }

    return render(request, 'advanced_learning/competitions/edit_answers.html', context)

@login_required
def delete_competition(request, competition_id):
    """Xóa cuộc thi"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)

    if request.method == 'POST':
        competition.delete()
        messages.success(request, 'Cuộc thi đã được xóa thành công!')
        return redirect('advanced_learning:competition_list')

    context = {
        'competition': competition,
    }

    return render(request, 'advanced_learning/competitions/delete.html', context)

# Hàm hỗ trợ
def update_competition_rankings(competition):
    """Cập nhật xếp hạng cho cuộc thi"""
    participants = CompetitionParticipant.objects.filter(competition=competition, end_time__isnull=False).order_by('-score')

    # Cập nhật xếp hạng
    rank = 1
    prev_score = None
    for i, participant in enumerate(participants):
        if prev_score is not None and participant.score < prev_score:
            rank = i + 1
        participant.rank = rank
        participant.save(update_fields=['rank'])
        prev_score = participant.score

# Hàm tạo thông báo
def create_notification(user, title, message, notification_type='info', related_feature='system', related_object_id=None, url=''):
    """Tạo thông báo mới cho người dùng"""
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        related_feature=related_feature,
        related_object_id=related_object_id,
        url=url
    )
    return notification

# Hàm tạo thông báo cho cuộc thi sắp diễn ra
def create_upcoming_competition_notifications():
    """Tạo thông báo cho các cuộc thi sắp diễn ra"""
    now = timezone.now()
    tomorrow = now + timedelta(days=1)

    # Tìm các cuộc thi sắp diễn ra trong vòng 24 giờ tới
    upcoming_competitions = CompetitionMode.objects.filter(
        start_time__gt=now,
        start_time__lte=tomorrow,
        is_active=True
    )

    for competition in upcoming_competitions:
        # Tìm các người dùng đã tham gia ít nhất một cuộc thi trước đó
        participants = User.objects.filter(competition_participations__isnull=False).distinct()

        for user in participants:
            # Kiểm tra xem người dùng đã có thông báo về cuộc thi này chưa
            existing_notification = Notification.objects.filter(
                user=user,
                related_feature='competition',
                related_object_id=competition.id,
                title__contains='sắp diễn ra'
            ).exists()

            if not existing_notification:
                # Tạo thông báo mới
                hours_to_start = int((competition.start_time - now).total_seconds() / 3600)
                create_notification(
                    user=user,
                    title=f'Cuộc thi sắp diễn ra: {competition.title}',
                    message=f'Cuộc thi {competition.title} sẽ bắt đầu sau {hours_to_start} giờ. Hãy chuẩn bị sẵn sàng!',
                    notification_type='info',
                    related_feature='competition',
                    related_object_id=competition.id,
                    url=reverse('advanced_learning:competition_detail', args=[competition.id])
                )

# Hàm tạo thông báo cho dự án chưa cập nhật
def create_project_update_reminders():
    """Tạo thông báo nhắc nhở cập nhật dự án"""
    now = timezone.now()
    one_week_ago = now - timedelta(days=7)

    # Tìm các dự án đang thực hiện nhưng chưa cập nhật trong 7 ngày qua
    stale_projects = UserProject.objects.filter(
        status='in_progress',
        updated_at__lt=one_week_ago
    )

    for project in stale_projects:
        # Kiểm tra xem người dùng đã có thông báo về dự án này chưa
        existing_notification = Notification.objects.filter(
            user=project.user,
            related_feature='project',
            related_object_id=project.id,
            created_at__gt=one_week_ago,
            title__contains='cập nhật'
        ).exists()

        if not existing_notification:
            # Tạo thông báo mới
            days_since_update = (now - project.updated_at).days
            create_notification(
                user=project.user,
                title=f'Nhắc nhở cập nhật dự án: {project.project.title}',
                message=f'Dự án {project.project.title} của bạn chưa được cập nhật trong {days_since_update} ngày. Hãy cập nhật tiến độ để duy trì đà học tập!',
                notification_type='warning',
                related_feature='project',
                related_object_id=project.id,
                url=reverse('advanced_learning:project_detail', args=[project.project.id])
            )

# Trang thống kê và phân tích học tập
@login_required
def learning_analytics(request):
    """Trang thống kê và phân tích học tập"""
    # Thống kê Pomodoro theo thời gian
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    pomodoro_sessions = PomodoroSession.objects.filter(user=request.user, end_time__gte=last_30_days)

    # Tạo dữ liệu cho biểu đồ Pomodoro theo ngày
    pomodoro_data = {}
    for i in range(30):
        date = (now - timedelta(days=i)).date()
        pomodoro_data[date] = 0

    for session in pomodoro_sessions:
        date = session.end_time.date()
        if date in pomodoro_data:
            # Tính thời gian dựa trên work_duration và completed_pomodoros
            pomodoro_data[date] += session.work_duration * session.completed_pomodoros

    # Chuyển đổi dữ liệu cho biểu đồ
    pomodoro_labels = [date.strftime('%d/%m') for date in sorted(pomodoro_data.keys())]
    pomodoro_values = [pomodoro_data[date] for date in sorted(pomodoro_data.keys())]

    # Thống kê sử dụng các tính năng học tập nâng cao
    feature_usage = {
        'Pomodoro': PomodoroSession.objects.filter(user=request.user).count(),
        'Cornell Notes': CornellNote.objects.filter(user=request.user).count(),
        'Mind Maps': MindMap.objects.filter(user=request.user).count(),
        'Feynman Notes': FeynmanNote.objects.filter(user=request.user).count(),
        'Projects': UserProject.objects.filter(user=request.user).count(),
        'Competitions': CompetitionParticipant.objects.filter(user=request.user).count(),
    }

    # Tổng số phút học tập (Pomodoro)
    # Tính tổng thời gian làm việc dựa trên work_duration và completed_pomodoros
    total_study_minutes = 0
    for session in PomodoroSession.objects.filter(user=request.user, end_time__isnull=False):
        total_study_minutes += session.work_duration * session.completed_pomodoros

    # Tổng số điểm thi đấu
    total_competition_points = CompetitionParticipant.objects.filter(user=request.user, end_time__isnull=False).aggregate(total=Sum('score'))['total'] or 0

    # Tiến độ dự án trung bình
    avg_project_progress = UserProject.objects.filter(user=request.user).aggregate(avg=Avg('progress'))['avg'] or 0

    # Phân tích xu hướng học tập
    learning_trends = {
        'pomodoro_trend': calculate_trend(pomodoro_values[-7:]) if len(pomodoro_values) >= 7 else 0,
        'notes_trend': calculate_notes_trend(request.user),
        'project_trend': calculate_project_trend(request.user),
    }

    context = {
        'pomodoro_labels': pomodoro_labels,
        'pomodoro_values': pomodoro_values,
        'feature_usage': feature_usage,
        'total_study_minutes': total_study_minutes,
        'total_competition_points': total_competition_points,
        'avg_project_progress': avg_project_progress,
        'learning_trends': learning_trends,
    }

    return render(request, 'advanced_learning/analytics.html', context)

# Hàm tính toán xu hướng
def calculate_trend(values):
    """Tính toán xu hướng tăng/giảm"""
    if not values or len(values) < 2:
        return 0

    # Tính tổng sự thay đổi
    changes = [values[i] - values[i-1] for i in range(1, len(values))]
    avg_change = sum(changes) / len(changes)

    # Chuẩn hóa xu hướng về khoảng -1 đến 1
    if avg_change == 0:
        return 0

    max_possible_change = max(values) if max(values) > 0 else 1
    normalized_trend = avg_change / max_possible_change

    # Giới hạn giá trị trong khoảng -1 đến 1
    return max(min(normalized_trend, 1), -1)

def calculate_notes_trend(user):
    """Tính toán xu hướng sử dụng ghi chú"""
    now = timezone.now()
    last_week = now - timedelta(days=7)
    week_before = last_week - timedelta(days=7)

    # Đếm số ghi chú trong tuần trước
    notes_last_week = (
        CornellNote.objects.filter(user=user, created_at__gte=last_week, created_at__lte=now).count() +
        FeynmanNote.objects.filter(user=user, created_at__gte=last_week, created_at__lte=now).count() +
        MindMap.objects.filter(user=user, created_at__gte=last_week, created_at__lte=now).count()
    )

    # Đếm số ghi chú trong tuần trước nữa
    notes_week_before = (
        CornellNote.objects.filter(user=user, created_at__gte=week_before, created_at__lte=last_week).count() +
        FeynmanNote.objects.filter(user=user, created_at__gte=week_before, created_at__lte=last_week).count() +
        MindMap.objects.filter(user=user, created_at__gte=week_before, created_at__lte=last_week).count()
    )

    # Tính xu hướng
    if notes_week_before == 0:
        return 0 if notes_last_week == 0 else 1

    change = (notes_last_week - notes_week_before) / notes_week_before
    return max(min(change, 1), -1)

def calculate_project_trend(user):
    """Tính toán xu hướng tiến độ dự án"""
    projects = UserProject.objects.filter(user=user)

    if not projects.exists():
        return 0

    # Lấy các dự án đang thực hiện
    in_progress_projects = projects.filter(status='in_progress')

    if not in_progress_projects.exists():
        return 0

    # Tính tiến độ trung bình
    avg_progress = in_progress_projects.aggregate(avg=Avg('progress'))['avg'] or 0

    # Đánh giá xu hướng dựa trên tiến độ trung bình
    if avg_progress < 25:
        return -0.5  # Tiến độ chậm
    elif avg_progress < 50:
        return 0     # Tiến độ trung bình
    elif avg_progress < 75:
        return 0.5   # Tiến độ tốt
    else:
        return 1     # Tiến độ rất tốt

# Trang thông báo
@login_required
def notifications(request):
    """Trang hiển thị thông báo của người dùng"""
    # Lấy tất cả thông báo của người dùng
    user_notifications = Notification.objects.filter(user=request.user)

    # Đánh dấu tất cả thông báo đã đọc nếu có tham số mark_all_read
    if request.GET.get('mark_all_read'):
        user_notifications.update(is_read=True)
        messages.success(request, 'Đã đánh dấu tất cả thông báo là đã đọc.')
        return redirect('advanced_learning:notifications')

    # Xóa tất cả thông báo đã đọc nếu có tham số delete_read
    if request.GET.get('delete_read'):
        user_notifications.filter(is_read=True).delete()
        messages.success(request, 'Đã xóa tất cả thông báo đã đọc.')
        return redirect('advanced_learning:notifications')

    # Phân trang
    page = request.GET.get('page', 1)
    paginator = Paginator(user_notifications, 10)  # 10 thông báo mỗi trang

    try:
        notifications_page = paginator.page(page)
    except PageNotAnInteger:
        notifications_page = paginator.page(1)
    except EmptyPage:
        notifications_page = paginator.page(paginator.num_pages)

    context = {
        'notifications': notifications_page,
        'unread_count': user_notifications.filter(is_read=False).count(),
    }

    return render(request, 'advanced_learning/notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Đánh dấu thông báo là đã đọc và chuyển hướng đến URL của thông báo"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)

    # Đánh dấu thông báo là đã đọc
    notification.is_read = True
    notification.save()

    # Chuyển hướng đến URL của thông báo nếu có
    if notification.url:
        return redirect(notification.url)
    else:
        return redirect('advanced_learning:notifications')

@login_required
def delete_notification(request, notification_id):
    """Xóa thông báo"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    messages.success(request, 'Đã xóa thông báo.')
    return redirect('advanced_learning:notifications')

@login_required
def get_unread_notifications_count(request):
    """Trả về số lượng thông báo chưa đọc dưới dạng JSON"""
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})

# Trang tổng quan (Dashboard)
@login_required
def dashboard(request):
    """Trang tổng quan cho người dùng"""
    # Tạo thông báo cho cuộc thi sắp diễn ra và dự án chưa cập nhật
    create_upcoming_competition_notifications()
    create_project_update_reminders()

    # Thống kê Pomodoro
    pomodoro_sessions = PomodoroSession.objects.filter(user=request.user)
    total_pomodoro_sessions = pomodoro_sessions.count()

    # Tính tổng thời gian làm việc dựa trên work_duration và completed_pomodoros
    total_pomodoro_minutes = 0
    for session in pomodoro_sessions:
        if session.end_time:  # Chỉ tính các phiên đã hoàn thành
            total_pomodoro_minutes += session.work_duration * session.completed_pomodoros

    recent_pomodoro_sessions = pomodoro_sessions.order_by('-end_time')[:5]

    # Thống kê ghi chú Cornell
    cornell_notes = CornellNote.objects.filter(user=request.user)
    total_cornell_notes = cornell_notes.count()
    recent_cornell_notes = cornell_notes.order_by('-created_at')[:5]

    # Thống kê Mind Map
    mind_maps = MindMap.objects.filter(user=request.user)
    total_mind_maps = mind_maps.count()
    recent_mind_maps = mind_maps.order_by('-created_at')[:5]

    # Thống kê Feynman Notes
    feynman_notes = FeynmanNote.objects.filter(user=request.user)
    total_feynman_notes = feynman_notes.count()
    recent_feynman_notes = feynman_notes.order_by('-created_at')[:5]

    # Thống kê dự án
    user_projects = UserProject.objects.filter(user=request.user)
    total_projects = user_projects.count()
    completed_projects = user_projects.filter(status='completed').count()
    in_progress_projects = user_projects.filter(status='in_progress').count()
    recent_projects = user_projects.order_by('-started_at')[:5]

    # Thống kê cuộc thi
    participations = CompetitionParticipant.objects.filter(user=request.user)
    total_competitions = participations.count()
    completed_competitions = participations.filter(end_time__isnull=False).count()
    best_rank = participations.filter(rank__isnull=False).order_by('rank').first()
    recent_competitions = participations.order_by('-start_time')[:5]

    # Thống kê hoạt động gần đây
    recent_activities = []

    # Thêm Pomodoro sessions
    for session in recent_pomodoro_sessions:
        recent_activities.append({
            'type': 'pomodoro',
            'title': f'Phiên Pomodoro {session.duration} phút',
            'date': session.end_time,
            'url': reverse('advanced_learning:pomodoro_history'),
            'icon': 'fas fa-clock'
        })

    # Thêm Cornell notes
    for note in recent_cornell_notes:
        recent_activities.append({
            'type': 'cornell',
            'title': note.title,
            'date': note.created_at,
            'url': reverse('advanced_learning:cornell_note_detail', args=[note.id]),
            'icon': 'fas fa-sticky-note'
        })

    # Thêm Mind maps
    for mind_map in recent_mind_maps:
        recent_activities.append({
            'type': 'mindmap',
            'title': mind_map.title,
            'date': mind_map.created_at,
            'url': reverse('advanced_learning:mind_map_detail', args=[mind_map.id]),
            'icon': 'fas fa-project-diagram'
        })

    # Thêm Feynman notes
    for note in recent_feynman_notes:
        recent_activities.append({
            'type': 'feynman',
            'title': note.title,
            'date': note.created_at,
            'url': reverse('advanced_learning:feynman_note_detail', args=[note.id]),
            'icon': 'fas fa-lightbulb'
        })

    # Thêm Projects
    for project in recent_projects:
        recent_activities.append({
            'type': 'project',
            'title': project.project.title,
            'date': project.started_at,
            'url': reverse('advanced_learning:project_detail', args=[project.project.id]),
            'icon': 'fas fa-tasks'
        })

    # Thêm Competitions
    for competition in recent_competitions:
        recent_activities.append({
            'type': 'competition',
            'title': competition.competition.title,
            'date': competition.start_time,
            'url': reverse('advanced_learning:competition_detail', args=[competition.competition.id]),
            'icon': 'fas fa-trophy'
        })

    # Sắp xếp hoạt động theo thời gian gần đây nhất
    recent_activities.sort(key=lambda x: x['date'], reverse=True)
    recent_activities = recent_activities[:10]  # Chỉ lấy 10 hoạt động gần đây nhất

    # Thông báo chưa đọc
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]

    context = {
        'total_pomodoro_sessions': total_pomodoro_sessions,
        'total_pomodoro_minutes': total_pomodoro_minutes,
        'total_cornell_notes': total_cornell_notes,
        'total_mind_maps': total_mind_maps,
        'total_feynman_notes': total_feynman_notes,
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'in_progress_projects': in_progress_projects,
        'total_competitions': total_competitions,
        'completed_competitions': completed_competitions,
        'best_rank': best_rank,
        'recent_activities': recent_activities,
        'unread_notifications': unread_notifications,
        'unread_notifications_count': unread_notifications.count(),
    }

    return render(request, 'advanced_learning/dashboard.html', context)
