from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Sum, F, ExpressionWrapper, fields, Avg, Min
from django.forms import inlineformset_factory
from django.template.loader import render_to_string, get_template
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.mail import send_mail
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from datetime import timedelta
import io
import json
import uuid
import sys
import time
from xhtml2pdf import pisa
from .models import PomodoroSession, CornellNote, MindMap, FeynmanNote, Project, ProjectTask, UserProject, InteractiveExercise, CompetitionMode, CompetitionQuestion, CompetitionAnswer, CompetitionParticipant, Notification, ProjectComment, Achievement, UserAchievement, ExerciseSubmission, CompetitionSubscription, CompetitionTeam, LiveCompetition, LiveParticipant, CompetitionAchievement
from .forms import CornellNoteForm, MindMapForm, FeynmanNoteForm, ProjectForm, ProjectTaskForm, UserProjectForm, InteractiveExerciseForm, CompetitionForm, CompetitionQuestionForm, CompetitionAnswerForm, CompetitionParticipantForm
from content.models import Subject, Topic, Lesson
from flashcards.models import FlashcardSet, Flashcard
from quizzes.models import Quiz, Question, Answer

# Pomodoro Timer Views
@login_required
def get_topics(request):
    """Lấy danh sách các chủ đề con theo chủ đề chính"""
    subject_id = request.GET.get('subject', '')
    topics = []

    if subject_id:
        topics = Topic.objects.filter(subject_id=subject_id)

    return render(request, 'advanced_learning/pomodoro/topic_options.html', {'topics': topics})

@login_required
def pomodoro_timer(request):
    """Hiển thị trang Pomodoro Timer"""
    subjects = Subject.objects.all()
    topics = Topic.objects.none()  # Sẽ được cập nhật bằng HTMX khi chọn subject
    format_type = request.GET.get('format', '')
    session_id = request.GET.get('session_id')

    # Lấy phiên Pomodoro đang hoạt động nếu có
    active_session = PomodoroSession.objects.filter(
        user=request.user,
        end_time__isnull=True
    ).first()

    # Lấy dữ liệu cho biểu đồ thời gian học tập theo ngày
    today = timezone.now().date()
    start_date = today - timedelta(days=6)  # 7 ngày gần nhất (bao gồm hôm nay)

    # Tạo danh sách các ngày
    date_labels = []
    date_data = []

    for i in range(7):
        date = start_date + timedelta(days=i)
        date_labels.append(date.strftime('%d/%m'))

        # Tính tổng thời gian học tập trong ngày (phút)
        daily_sessions = PomodoroSession.objects.filter(
            user=request.user,
            start_time__date=date,
            end_time__isnull=False
        )

        total_minutes = 0
        for session in daily_sessions:
            duration = (session.end_time - session.start_time).total_seconds() // 60
            total_minutes += duration

        date_data.append(total_minutes)

    # Dữ liệu cho biểu đồ phân bố thời gian theo chủ đề
    subject_sessions = PomodoroSession.objects.filter(
        user=request.user,
        end_time__isnull=False,
        subject__isnull=False
    ).values('subject__name').annotate(
        total_duration=Sum(ExpressionWrapper(
            F('end_time') - F('start_time'),
            output_field=fields.DurationField()
        ))
    )

    subject_labels = []
    subject_data = []

    for item in subject_sessions:
        subject_labels.append(item['subject__name'])
        # Chuyển đổi từ timedelta sang phút
        minutes = item['total_duration'].total_seconds() // 60
        subject_data.append(minutes)

    # Nếu không có dữ liệu, thêm dữ liệu mẫu
    if not subject_labels:
        subject_labels = ['Chưa có dữ liệu']
        subject_data = [0]

    # Chuẩn bị dữ liệu cho biểu đồ
    daily_chart_data = {
        'labels': date_labels,
        'data': date_data
    }

    subject_chart_data = {
        'labels': subject_labels,
        'data': subject_data
    }

    import json

    # Nếu có session_id, lấy thông tin phiên cụ thể
    template_session = None
    if session_id:
        try:
            template_session = PomodoroSession.objects.get(id=session_id, user=request.user)
        except PomodoroSession.DoesNotExist:
            pass

    context = {
        'subjects': subjects,
        'topics': topics,
        'active_session': active_session,
        'template_session': template_session,
        'work_duration': 25,  # Mặc định 25 phút
        'break_duration': 5,  # Mặc định 5 phút
        'daily_chart_data': json.dumps(daily_chart_data),
        'subject_chart_data': json.dumps(subject_chart_data),
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/pomodoro/timer_partial.html', context)

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

    # Kiểm tra nếu là request HTMX
    if request.htmx:
        # Chuyển hướng đến trang lịch sử Pomodoro với HTMX
        return redirect('advanced_learning:pomodoro_history')

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
    # Lấy tham số từ request
    format_type = request.GET.get('format', '')
    subject_id = request.GET.get('subject', '')
    date_str = request.GET.get('date', '')

    # Lấy tất cả các phiên Pomodoro của người dùng, sắp xếp theo thời gian bắt đầu giảm dần
    sessions = PomodoroSession.objects.filter(user=request.user).order_by('-start_time')

    # Áp dụng bộ lọc
    if subject_id:
        sessions = sessions.filter(subject_id=subject_id)

    if date_str:
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            sessions = sessions.filter(start_time__date=date_obj)
        except (ValueError, TypeError):
            pass

    # Tính tổng thời gian học tập
    total_minutes = 0
    total_pomodoros = 0

    for session in sessions:
        if session.end_time:  # Chỉ tính các phiên đã kết thúc
            duration = (session.end_time - session.start_time).total_seconds() // 60  # Thời gian tính bằng phút
            total_minutes += duration
            total_pomodoros += session.completed_pomodoros

    # Lấy danh sách các chủ đề cho bộ lọc
    subjects = Subject.objects.all()

    # Tạo dữ liệu cho biểu đồ
    from datetime import timedelta
    import json

    # Lấy 7 ngày gần nhất
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)

    # Tạo danh sách các ngày
    date_range = [start_date + timedelta(days=i) for i in range(7)]
    date_labels = [date.strftime('%d/%m') for date in date_range]

    # Đếm số phiên và thời gian theo ngày
    sessions_by_date = {}
    minutes_by_date = {}
    for date in date_range:
        sessions_by_date[date] = 0
        minutes_by_date[date] = 0

    for session in sessions:
        if not session.end_time:
            continue

        session_date = session.start_time.date()
        if start_date <= session_date <= end_date:
            if session_date in sessions_by_date:
                sessions_by_date[session_date] += 1
                # Tính tổng số phút làm việc
                minutes_by_date[session_date] += session.work_duration * session.completed_pomodoros

    # Chuyển đổi thành danh sách cho biểu đồ
    chart_data = [sessions_by_date[date] for date in date_range]
    chart_minutes = [minutes_by_date[date] for date in date_range]

    context = {
        'sessions': sessions,
        'subjects': subjects,
        'selected_subject': subject_id,
        'selected_date': date_str,
        'total_minutes': total_minutes,
        'total_hours': total_minutes // 60,
        'remaining_minutes': total_minutes % 60,
        'total_pomodoros': total_pomodoros,
        'chart_labels': json.dumps(date_labels),
        'chart_data': json.dumps(chart_data),
        'chart_minutes': json.dumps(chart_minutes),
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/pomodoro/history_partial.html', context)

    return render(request, 'advanced_learning/pomodoro/history.html', context)

# Hệ thống ghi chú Cornell Views
@login_required
def cornell_note_list(request):
    """Hiển thị danh sách ghi chú Cornell của người dùng"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    format_type = request.GET.get('format', '')
    view_type = request.GET.get('view', 'grid')  # Mặc định là chế độ lưới

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

    # Đếm số ghi chú cần ôn tập
    now = timezone.now()
    notes_to_review_count = CornellNote.objects.filter(
        user=request.user,
        next_review_date__lte=now
    ).count()

    # Lấy danh sách các chủ đề cho bộ lọc
    subjects = Subject.objects.all()

    context = {
        'notes': notes,
        'subjects': subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
        'notes_to_review_count': notes_to_review_count,
        'view': view_type,
        'now': now,  # Thêm thời gian hiện tại để so sánh với next_review_date
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/cornell_notes/list_partial.html', context)

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
    format_type = request.GET.get('format', '')

    # Lấy thời gian hiện tại để so sánh với next_review_date
    now = timezone.now()

    context = {
        'note': note,
        'now': now,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/cornell_notes/detail_partial.html', context)

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

    # Xử lý HTMX DELETE request
    if request.method == 'DELETE' or (request.method == 'POST' and request.htmx):
        note.delete()
        messages.success(request, 'Ghi chú Cornell đã được xóa thành công!')

        # Nếu là request HTMX, trả về danh sách partial
        if request.htmx:
            # Lấy các tham số tìm kiếm và lọc
            search_query = request.GET.get('search', '')
            subject_id = request.GET.get('subject', '')
            view_type = request.GET.get('view', 'grid')

            # Lấy danh sách ghi chú mới
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

            # Đếm số ghi chú cần ôn tập
            now = timezone.now()
            notes_to_review_count = CornellNote.objects.filter(
                user=request.user,
                next_review_date__lte=now
            ).count()

            context = {
                'notes': notes,
                'subjects': subjects,
                'search_query': search_query,
                'selected_subject': subject_id,
                'notes_to_review_count': notes_to_review_count,
                'view': view_type,
                'now': now,
            }

            return render(request, 'advanced_learning/cornell_notes/list_partial.html', context)

        return redirect('advanced_learning:cornell_note_list')

    # Xử lý POST request bình thường
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Ghi chú Cornell đã được xóa thành công!')
        return redirect('advanced_learning:cornell_note_list')

    context = {
        'note': note,
    }

    return render(request, 'advanced_learning/cornell_notes/delete.html', context)

# Tính năng mới cho Cornell Notes
@login_required
def cornell_note_export_pdf(request, note_id):
    """Xuất ghi chú Cornell sang PDF"""
    note = get_object_or_404(CornellNote, id=note_id, user=request.user)

    # Tạo template HTML
    template = get_template('advanced_learning/cornell_notes/pdf_template.html')
    context = {'note': note}
    html = template.render(context)

    # Tạo file PDF từ HTML
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        # Trả về file PDF
        result.seek(0)
        filename = f"cornell_note_{note.id}.pdf"
        response = FileResponse(result, as_attachment=True, filename=filename)
        return response

    # Nếu có lỗi
    messages.error(request, 'Có lỗi khi tạo file PDF. Vui lòng thử lại sau.')
    return redirect('advanced_learning:cornell_note_detail', note_id=note.id)

@login_required
def cornell_note_share(request, note_id):
    """Chia sẻ ghi chú Cornell"""
    note = get_object_or_404(CornellNote, id=note_id, user=request.user)

    if request.method == 'POST':
        # Tạo URL chia sẻ nếu chưa có
        if not note.share_url:
            note.generate_share_url()

        # Đánh dấu ghi chú là đã chia sẻ
        note.is_shared = True
        note.save(update_fields=['is_shared'])

        # Gửi email chia sẻ nếu có email
        email = request.POST.get('email')
        if email:
            share_url = request.build_absolute_uri(reverse('advanced_learning:cornell_note_shared_view', args=[note.share_url]))
            subject = f"{request.user.username} đã chia sẻ ghi chú Cornell với bạn"
            message = f"Xin chào,\n\n{request.user.username} đã chia sẻ ghi chú Cornell '{note.title}' với bạn.\n\nBạn có thể xem ghi chú tại: {share_url}\n\nTrân trọng,\nNền Tảng Học Tập"

            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                messages.success(request, f'Đã chia sẻ ghi chú với {email}.')
            except Exception as e:
                messages.error(request, f'Không thể gửi email: {str(e)}')

        messages.success(request, 'Ghi chú đã được chia sẻ thành công!')
        return redirect('advanced_learning:cornell_note_detail', note_id=note.id)

    context = {
        'note': note,
        'share_url': request.build_absolute_uri(reverse('advanced_learning:cornell_note_shared_view', args=[note.share_url])) if note.share_url else None
    }

    return render(request, 'advanced_learning/cornell_notes/share.html', context)

def cornell_note_shared_view(request, share_url):
    """Xem ghi chú Cornell được chia sẻ"""
    note = get_object_or_404(CornellNote, share_url=share_url, is_shared=True)

    context = {
        'note': note,
        'is_shared_view': True
    }

    return render(request, 'advanced_learning/cornell_notes/shared_view.html', context)

@login_required
def cornell_note_review(request, note_id):
    """Ôn tập ghi chú Cornell"""
    note = get_object_or_404(CornellNote, id=note_id, user=request.user)

    if request.method == 'POST':
        # Đánh dấu đã ôn tập
        note.mark_reviewed()
        messages.success(request, 'Ghi chú đã được đánh dấu là đã ôn tập!')

        # Chuyển hướng đến trang danh sách cần ôn tập hoặc chi tiết
        next_url = request.POST.get('next', '')
        if next_url == 'to_review':
            return redirect('advanced_learning:cornell_notes_to_review')
        return redirect('advanced_learning:cornell_note_detail', note_id=note.id)

    context = {
        'note': note,
        'is_review': True,
        'next': request.GET.get('next', '')
    }

    return render(request, 'advanced_learning/cornell_notes/review.html', context)

@login_required
def cornell_notes_to_review(request):
    """Danh sách ghi chú Cornell cần ôn tập"""
    # Lấy các ghi chú cần ôn tập (next_review_date <= now)
    now = timezone.now()
    notes_to_review = CornellNote.objects.filter(
        user=request.user,
        next_review_date__lte=now
    ).order_by('next_review_date')

    context = {
        'notes': notes_to_review,
        'is_review_list': True
    }

    return render(request, 'advanced_learning/cornell_notes/to_review.html', context)

@login_required
def cornell_note_create_flashcards(request, note_id):
    """Tạo flashcards từ ghi chú Cornell"""
    note = get_object_or_404(CornellNote, id=note_id, user=request.user)

    if request.method == 'POST':
        # Tạo bộ flashcard mới
        flashcard_set = FlashcardSet.objects.create(
            user=request.user,
            title=f"Flashcards từ {note.title}",
            description=f"Tạo tự động từ ghi chú Cornell: {note.title}"
        )

        # Tạo các flashcard từ cột gợi ý và ghi chú chính
        cues = note.cue_column.strip().split('\n')
        main_notes = note.main_notes.strip().split('\n')

        # Nếu có cột gợi ý, sử dụng làm mặt trước và ghi chú chính làm mặt sau
        if note.cue_column.strip():
            for i, cue in enumerate(cues):
                if cue.strip():
                    Flashcard.objects.create(
                        flashcard_set=flashcard_set,
                        front=cue.strip(),
                        back=main_notes[i].strip() if i < len(main_notes) else "",
                        order=i+1
                    )
        # Nếu không có cột gợi ý, tạo flashcard từ ghi chú chính
        else:
            for i, line in enumerate(main_notes):
                if ':' in line:
                    parts = line.split(':', 1)
                    front = parts[0].strip()
                    back = parts[1].strip()
                    Flashcard.objects.create(
                        flashcard_set=flashcard_set,
                        front=front,
                        back=back,
                        order=i+1
                    )

        messages.success(request, f'Đã tạo {flashcard_set.flashcards.count()} flashcard từ ghi chú Cornell!')
        return redirect('flashcards:flashcard_set_detail', set_id=flashcard_set.id)

    context = {
        'note': note
    }

    return render(request, 'advanced_learning/cornell_notes/create_flashcards.html', context)

@login_required
def cornell_note_create_quiz(request, note_id):
    """Tạo quiz từ ghi chú Cornell"""
    note = get_object_or_404(CornellNote, id=note_id, user=request.user)

    if request.method == 'POST':
        # Tạo quiz mới
        quiz = Quiz.objects.create(
            user=request.user,
            title=f"Quiz từ {note.title}",
            description=f"Tạo tự động từ ghi chú Cornell: {note.title}",
            time_limit=10,  # 10 phút
            pass_percentage=70  # 70%
        )

        # Tạo câu hỏi từ cột gợi ý
        if note.cue_column.strip():
            cues = note.cue_column.strip().split('\n')
            for i, cue in enumerate(cues):
                if cue.strip() and '?' in cue:
                    # Tạo câu hỏi
                    question = Question.objects.create(
                        quiz=quiz,
                        text=cue.strip(),
                        order=i+1
                    )

                    # Tạo câu trả lời đúng từ ghi chú chính
                    main_notes = note.main_notes.strip().split('\n')
                    correct_answer = main_notes[i].strip() if i < len(main_notes) else ""

                    Answer.objects.create(
                        question=question,
                        text=correct_answer,
                        is_correct=True
                    )

                    # Tạo các câu trả lời sai (giả)
                    for j in range(3):  # Thêm 3 câu trả lời sai
                        fake_index = (i + j + 1) % len(main_notes)
                        fake_answer = main_notes[fake_index].strip()
                        if fake_answer != correct_answer:
                            Answer.objects.create(
                                question=question,
                                text=fake_answer,
                                is_correct=False
                            )

        messages.success(request, f'Đã tạo quiz với {quiz.questions.count()} câu hỏi từ ghi chú Cornell!')
        return redirect('quizzes:quiz_detail', quiz_id=quiz.id)

    context = {
        'note': note
    }

    return render(request, 'advanced_learning/cornell_notes/create_quiz.html', context)

# Hệ thống Mind Mapping Views
@login_required
def mind_map_list(request):
    """Hiển thị danh sách sơ đồ tư duy của người dùng"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    format_type = request.GET.get('format', '')
    view_type = request.GET.get('view', 'grid')  # Mặc định là chế độ lưới

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
        'view': view_type,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/mind_maps/list_partial.html', context)

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
    format_type = request.GET.get('format', '')

    # Đếm số nút trong sơ đồ tư duy
    node_count = 0
    if mind_map.map_data:
        # Hàm đệ quy đếm số nút
        def count_nodes(node):
            count = 1  # Đếm nút hiện tại
            if 'children' in node:
                for child in node['children']:
                    count += count_nodes(child)
            return count

        # Đếm từ nút gốc
        try:
            node_count = count_nodes(mind_map.map_data)
        except Exception:
            node_count = 1

    context = {
        'mind_map': mind_map,
        'node_count': node_count,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/mind_maps/detail_partial.html', context)

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

    # Xử lý HTMX DELETE request
    if request.method == 'DELETE' or (request.method == 'POST' and request.htmx):
        mind_map.delete()
        messages.success(request, 'Sơ đồ tư duy đã được xóa thành công!')

        # Nếu là request HTMX, trả về danh sách partial
        if request.htmx:
            # Lấy các tham số tìm kiếm và lọc
            search_query = request.GET.get('search', '')
            subject_id = request.GET.get('subject', '')
            view_type = request.GET.get('view', 'grid')

            # Lấy danh sách sơ đồ tư duy mới
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
                'view': view_type,
            }

            return render(request, 'advanced_learning/mind_maps/list_partial.html', context)

        return redirect('advanced_learning:mind_map_list')

    # Xử lý POST request bình thường
    if request.method == 'POST':
        mind_map.delete()
        messages.success(request, 'Sơ đồ tư duy đã được xóa thành công!')
        return redirect('advanced_learning:mind_map_list')

    context = {
        'mind_map': mind_map,
    }

    return render(request, 'advanced_learning/mind_maps/delete.html', context)

# Tính năng mới cho Mind Mapping
@login_required
def mind_map_export_image(request, map_id):
    """Xuất sơ đồ tư duy sang hình ảnh"""
    mind_map = get_object_or_404(MindMap, id=map_id, user=request.user)

    if request.method == 'POST':
        # Lấy dữ liệu hình ảnh từ request
        image_data = request.POST.get('image_data', '')

        if image_data:
            # Xử lý dữ liệu hình ảnh Base64
            import base64
            from django.core.files.base import ContentFile

            # Loại bỏ phần header của dữ liệu Base64
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]

            # Tạo file hình ảnh
            data = ContentFile(base64.b64decode(imgstr))
            filename = f"mind_map_{mind_map.id}.{ext}"

            # Trả về file hình ảnh
            response = HttpResponse(data, content_type=f'image/{ext}')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

    # Nếu không phải POST hoặc không có dữ liệu hình ảnh
    messages.error(request, 'Không thể xuất hình ảnh. Vui lòng thử lại.')
    return redirect('advanced_learning:mind_map_detail', map_id=mind_map.id)

@login_required
def mind_map_export_pdf(request, map_id):
    """Xuất sơ đồ tư duy sang PDF"""
    mind_map = get_object_or_404(MindMap, id=map_id, user=request.user)

    # Tạo template HTML
    template = get_template('advanced_learning/mind_maps/pdf_template.html')
    context = {'mind_map': mind_map}
    html = template.render(context)

    # Tạo file PDF từ HTML
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        # Trả về file PDF
        result.seek(0)
        filename = f"mind_map_{mind_map.id}.pdf"
        response = FileResponse(result, as_attachment=True, filename=filename)
        return response

    # Nếu có lỗi
    messages.error(request, 'Có lỗi khi tạo file PDF. Vui lòng thử lại sau.')
    return redirect('advanced_learning:mind_map_detail', map_id=mind_map.id)

@login_required
def mind_map_share(request, map_id):
    """Chia sẻ sơ đồ tư duy"""
    mind_map = get_object_or_404(MindMap, id=map_id, user=request.user)

    if request.method == 'POST':
        # Tạo URL chia sẻ nếu chưa có
        if not mind_map.share_url:
            mind_map.generate_share_url()

        # Đánh dấu sơ đồ tư duy là đã chia sẻ
        mind_map.is_shared = True
        mind_map.save(update_fields=['is_shared'])

        # Gửi email chia sẻ nếu có email
        email = request.POST.get('email')
        if email:
            share_url = request.build_absolute_uri(reverse('advanced_learning:mind_map_shared_view', args=[mind_map.share_url]))
            subject = f"{request.user.username} đã chia sẻ sơ đồ tư duy với bạn"
            message = f"Xin chào,\n\n{request.user.username} đã chia sẻ sơ đồ tư duy '{mind_map.title}' với bạn.\n\nBạn có thể xem sơ đồ tư duy tại: {share_url}\n\nTrân trọng,\nNền Tảng Học Tập"

            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                messages.success(request, f'Đã chia sẻ sơ đồ tư duy với {email}.')
            except Exception as e:
                messages.error(request, f'Không thể gửi email: {str(e)}')

        messages.success(request, 'Sơ đồ tư duy đã được chia sẻ thành công!')
        return redirect('advanced_learning:mind_map_detail', map_id=mind_map.id)

    context = {
        'mind_map': mind_map,
        'share_url': request.build_absolute_uri(reverse('advanced_learning:mind_map_shared_view', args=[mind_map.share_url])) if mind_map.share_url else None
    }

    return render(request, 'advanced_learning/mind_maps/share.html', context)

def mind_map_shared_view(request, share_url):
    """Xem sơ đồ tư duy được chia sẻ"""
    mind_map = get_object_or_404(MindMap, share_url=share_url, is_shared=True)

    context = {
        'mind_map': mind_map,
        'is_shared_view': True
    }

    return render(request, 'advanced_learning/mind_maps/shared_view.html', context)

@login_required
def mind_map_create_flashcards(request, map_id):
    """Tạo flashcards từ sơ đồ tư duy"""
    mind_map = get_object_or_404(MindMap, id=map_id, user=request.user)

    if request.method == 'POST':
        # Tạo bộ flashcard mới
        flashcard_set = FlashcardSet.objects.create(
            user=request.user,
            title=f"Flashcards từ {mind_map.title}",
            description=f"Tạo tự động từ sơ đồ tư duy: {mind_map.title}"
        )

        # Tạo các flashcard từ dữ liệu sơ đồ tư duy
        map_data = mind_map.map_data

        # Tạo flashcard cho chủ đề trung tâm
        Flashcard.objects.create(
            flashcard_set=flashcard_set,
            front=map_data.get('text', mind_map.central_topic),
            back="Chủ đề trung tâm của sơ đồ tư duy",
            order=1
        )

        # Tạo flashcard cho các nút con
        order = 2
        for child in map_data.get('children', []):
            if 'text' in child:
                Flashcard.objects.create(
                    flashcard_set=flashcard_set,
                    front=child.get('text', ''),
                    back=map_data.get('text', mind_map.central_topic),
                    order=order
                )
                order += 1

                # Tạo flashcard cho các nút cháu
                for grandchild in child.get('children', []):
                    if 'text' in grandchild:
                        Flashcard.objects.create(
                            flashcard_set=flashcard_set,
                            front=grandchild.get('text', ''),
                            back=child.get('text', ''),
                            order=order
                        )
                        order += 1

        messages.success(request, f'Đã tạo {flashcard_set.flashcards.count()} flashcard từ sơ đồ tư duy!')
        return redirect('flashcards:flashcard_set_detail', set_id=flashcard_set.id)

    context = {
        'mind_map': mind_map
    }

    return render(request, 'advanced_learning/mind_maps/create_flashcards.html', context)

@login_required
def mind_map_create_quiz(request, map_id):
    """Tạo quiz từ sơ đồ tư duy"""
    mind_map = get_object_or_404(MindMap, id=map_id, user=request.user)

    if request.method == 'POST':
        # Tạo quiz mới
        quiz = Quiz.objects.create(
            user=request.user,
            title=f"Quiz từ {mind_map.title}",
            description=f"Tạo tự động từ sơ đồ tư duy: {mind_map.title}",
            time_limit=10,  # 10 phút
            pass_percentage=70  # 70%
        )

        # Tạo các câu hỏi từ dữ liệu sơ đồ tư duy
        map_data = mind_map.map_data

        # Tạo câu hỏi cho chủ đề trung tâm
        central_topic = map_data.get('text', mind_map.central_topic)
        question = Question.objects.create(
            quiz=quiz,
            text=f"Chủ đề trung tâm của sơ đồ tư duy này là gì?",
            order=1
        )

        # Tạo câu trả lời đúng
        Answer.objects.create(
            question=question,
            text=central_topic,
            is_correct=True
        )

        # Tạo các câu trả lời sai
        children = map_data.get('children', [])
        for i, child in enumerate(children[:3]):
            if 'text' in child:
                Answer.objects.create(
                    question=question,
                    text=child.get('text', ''),
                    is_correct=False
                )

        # Tạo các câu hỏi cho các nút con
        for i, child in enumerate(children):
            if 'text' in child:
                child_text = child.get('text', '')
                question = Question.objects.create(
                    quiz=quiz,
                    text=f"{child_text} là một phần của chủ đề nào?",
                    order=i+2
                )

                # Tạo câu trả lời đúng
                Answer.objects.create(
                    question=question,
                    text=central_topic,
                    is_correct=True
                )

                # Tạo các câu trả lời sai
                for j, other_child in enumerate(children):
                    if 'text' in other_child and other_child.get('text', '') != child_text:
                        Answer.objects.create(
                            question=question,
                            text=other_child.get('text', ''),
                            is_correct=False
                        )
                        if j >= 2:  # Tối đa 3 câu trả lời sai
                            break

        messages.success(request, f'Đã tạo quiz với {quiz.questions.count()} câu hỏi từ sơ đồ tư duy!')
        return redirect('quizzes:quiz_detail', quiz_id=quiz.id)

    context = {
        'mind_map': mind_map
    }

    return render(request, 'advanced_learning/mind_maps/create_quiz.html', context)

@login_required
def mind_map_create_cornell_note(request, map_id):
    """Tạo ghi chú Cornell từ sơ đồ tư duy"""
    mind_map = get_object_or_404(MindMap, id=map_id, user=request.user)

    if request.method == 'POST':
        # Tạo ghi chú Cornell mới
        cornell_note = CornellNote.objects.create(
            user=request.user,
            title=f"Ghi chú từ {mind_map.title}",
            subject=mind_map.subject,
            main_notes="",
            cue_column="",
            summary=""
        )

        # Tạo nội dung ghi chú từ dữ liệu sơ đồ tư duy
        map_data = mind_map.map_data
        central_topic = map_data.get('text', mind_map.central_topic)

        # Tạo cột gợi ý và ghi chú chính
        cue_column = f"{central_topic}?\n"
        main_notes = f"{central_topic}:\n"

        # Thêm các nút con vào ghi chú
        for child in map_data.get('children', []):
            if 'text' in child:
                child_text = child.get('text', '')
                cue_column += f"- {child_text}?\n"
                main_notes += f"- {child_text}\n"

                # Thêm các nút cháu
                for grandchild in child.get('children', []):
                    if 'text' in grandchild:
                        grandchild_text = grandchild.get('text', '')
                        main_notes += f"  * {grandchild_text}\n"

        # Tạo tóm tắt
        summary = f"Sơ đồ tư duy '{mind_map.title}' tập trung vào chủ đề {central_topic} với các ý chính bao gồm: "
        child_texts = [child.get('text', '') for child in map_data.get('children', []) if 'text' in child]
        summary += ", ".join(child_texts) + "."

        # Cập nhật ghi chú Cornell
        cornell_note.main_notes = main_notes
        cornell_note.cue_column = cue_column
        cornell_note.summary = summary
        cornell_note.save()

        messages.success(request, 'Ghi chú Cornell đã được tạo thành công từ sơ đồ tư duy!')
        return redirect('advanced_learning:cornell_note_detail', note_id=cornell_note.id)

    context = {
        'mind_map': mind_map
    }

    return render(request, 'advanced_learning/mind_maps/create_cornell_note.html', context)

# Phương pháp Feynman Technique Views
@login_required
def feynman_note_list(request):
    """Hiển thị danh sách ghi chú Feynman của người dùng"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    format_type = request.GET.get('format', '')
    view_type = request.GET.get('view', 'grid')  # Mặc định là chế độ lưới

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

    # Đếm số ghi chú cần ôn tập
    now = timezone.now()
    notes_to_review_count = FeynmanNote.objects.filter(
        user=request.user,
        next_review_date__lte=now
    ).count()

    # Lấy danh sách các chủ đề cho bộ lọc
    subjects = Subject.objects.all()

    context = {
        'notes': notes,
        'subjects': subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
        'notes_to_review_count': notes_to_review_count,
        'view': view_type,
        'now': now,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/feynman_notes/list_partial.html', context)

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
    format_type = request.GET.get('format', '')

    # Lấy thời gian hiện tại để so sánh với next_review_date
    now = timezone.now()

    # Kiểm tra xem ghi chú có cần ôn tập không
    needs_review = note.next_review_date and note.next_review_date <= now

    context = {
        'note': note,
        'now': now,
        'needs_review': needs_review,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/feynman_notes/detail_partial.html', context)

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

    # Xử lý HTMX DELETE request
    if request.method == 'DELETE' or (request.method == 'POST' and request.htmx):
        note.delete()
        messages.success(request, 'Ghi chú Feynman đã được xóa thành công!')

        # Nếu là request HTMX, trả về danh sách partial
        if request.htmx:
            # Lấy các tham số tìm kiếm và lọc
            search_query = request.GET.get('search', '')
            subject_id = request.GET.get('subject', '')
            view_type = request.GET.get('view', 'grid')

            # Lấy danh sách ghi chú mới
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

            # Đếm số ghi chú cần ôn tập
            now = timezone.now()
            notes_to_review_count = FeynmanNote.objects.filter(
                user=request.user,
                next_review_date__lte=now
            ).count()

            context = {
                'notes': notes,
                'subjects': subjects,
                'search_query': search_query,
                'selected_subject': subject_id,
                'notes_to_review_count': notes_to_review_count,
                'view': view_type,
                'now': now,
            }

            return render(request, 'advanced_learning/feynman_notes/list_partial.html', context)

        return redirect('advanced_learning:feynman_note_list')

    # Xử lý POST request bình thường
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Ghi chú Feynman đã được xóa thành công!')
        return redirect('advanced_learning:feynman_note_list')

    context = {
        'note': note,
    }

    return render(request, 'advanced_learning/feynman_notes/delete.html', context)

# Tính năng mới cho Feynman Technique
@login_required
def feynman_note_export_pdf(request, note_id):
    """Xuất ghi chú Feynman sang PDF"""
    note = get_object_or_404(FeynmanNote, id=note_id, user=request.user)

    # Tạo template HTML
    template = get_template('advanced_learning/feynman_notes/pdf_template.html')
    context = {'note': note}
    html = template.render(context)

    # Tạo file PDF từ HTML
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        # Trả về file PDF
        result.seek(0)
        filename = f"feynman_note_{note.id}.pdf"
        response = FileResponse(result, as_attachment=True, filename=filename)
        return response

    # Nếu có lỗi
    messages.error(request, 'Có lỗi khi tạo file PDF. Vui lòng thử lại sau.')
    return redirect('advanced_learning:feynman_note_detail', note_id=note.id)

@login_required
def feynman_note_share(request, note_id):
    """Chia sẻ ghi chú Feynman"""
    note = get_object_or_404(FeynmanNote, id=note_id, user=request.user)

    if request.method == 'POST':
        # Tạo URL chia sẻ nếu chưa có
        if not note.share_url:
            note.generate_share_url()

        # Đánh dấu ghi chú là đã chia sẻ
        note.is_shared = True
        note.save(update_fields=['is_shared'])

        # Gửi email chia sẻ nếu có email
        email = request.POST.get('email')
        if email:
            share_url = request.build_absolute_uri(reverse('advanced_learning:feynman_note_shared_view', args=[note.share_url]))
            subject = f"{request.user.username} đã chia sẻ ghi chú Feynman với bạn"
            message = f"Xin chào,\n\n{request.user.username} đã chia sẻ ghi chú Feynman '{note.title}' với bạn.\n\nBạn có thể xem ghi chú tại: {share_url}\n\nTrân trọng,\nNền Tảng Học Tập"

            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                messages.success(request, f'Đã chia sẻ ghi chú với {email}.')
            except Exception as e:
                messages.error(request, f'Không thể gửi email: {str(e)}')

        messages.success(request, 'Ghi chú đã được chia sẻ thành công!')
        return redirect('advanced_learning:feynman_note_detail', note_id=note.id)

    context = {
        'note': note,
        'share_url': request.build_absolute_uri(reverse('advanced_learning:feynman_note_shared_view', args=[note.share_url])) if note.share_url else None
    }

    return render(request, 'advanced_learning/feynman_notes/share.html', context)

def feynman_note_shared_view(request, share_url):
    """Xem ghi chú Feynman được chia sẻ"""
    note = get_object_or_404(FeynmanNote, share_url=share_url, is_shared=True)

    context = {
        'note': note,
        'is_shared_view': True
    }

    return render(request, 'advanced_learning/feynman_notes/shared_view.html', context)

@login_required
def feynman_note_review(request, note_id):
    """\u00d4n tập ghi chú Feynman"""
    note = get_object_or_404(FeynmanNote, id=note_id, user=request.user)

    if request.method == 'POST':
        # Đánh dấu đã ôn tập
        note.mark_reviewed()
        messages.success(request, 'Đã đánh dấu ôn tập thành công!')

        # Chuyển hướng đến trang chi tiết hoặc danh sách cần ôn tập
        next_url = request.POST.get('next', '')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect('advanced_learning:feynman_note_detail', note_id=note.id)

    context = {
        'note': note,
        'next': request.GET.get('next', '')
    }

    return render(request, 'advanced_learning/feynman_notes/review.html', context)

@login_required
def feynman_notes_to_review(request):
    """Danh sách ghi chú Feynman cần ôn tập"""
    now = timezone.now()
    notes = FeynmanNote.objects.filter(
        user=request.user,
        next_review_date__lte=now
    ).order_by('next_review_date')

    context = {
        'notes': notes
    }

    return render(request, 'advanced_learning/feynman_notes/to_review.html', context)

@login_required
def feynman_note_create_flashcards(request, note_id):
    """Tạo flashcards từ ghi chú Feynman"""
    note = get_object_or_404(FeynmanNote, id=note_id, user=request.user)

    if request.method == 'POST':
        # Tạo bộ flashcard mới
        flashcard_set = FlashcardSet.objects.create(
            user=request.user,
            title=f"Flashcards từ {note.title}",
            description=f"Tạo tự động từ ghi chú Feynman: {note.title}"
        )

        # Tạo flashcard cho khái niệm
        Flashcard.objects.create(
            flashcard_set=flashcard_set,
            front=note.title,
            back=note.concept,
            order=1
        )

        # Tạo flashcard cho giải thích
        Flashcard.objects.create(
            flashcard_set=flashcard_set,
            front=f"Giải thích {note.title} bằng ngôn ngữ đơn giản",
            back=note.explanation,
            order=2
        )

        # Tạo flashcard cho lỗ hổng kiến thức nếu có
        if note.gaps_identified:
            Flashcard.objects.create(
                flashcard_set=flashcard_set,
                front=f"Lỗ hổng kiến thức về {note.title}",
                back=note.gaps_identified,
                order=3
            )

        # Tạo flashcard cho giải thích đã cải thiện nếu có
        if note.refined_explanation:
            Flashcard.objects.create(
                flashcard_set=flashcard_set,
                front=f"Giải thích nâng cao về {note.title}",
                back=note.refined_explanation,
                order=4
            )

        messages.success(request, f'Đã tạo {flashcard_set.flashcards.count()} flashcard từ ghi chú Feynman!')
        return redirect('flashcards:flashcard_set_detail', set_id=flashcard_set.id)

    context = {
        'note': note
    }

    return render(request, 'advanced_learning/feynman_notes/create_flashcards.html', context)

@login_required
def feynman_note_create_quiz(request, note_id):
    """Tạo quiz từ ghi chú Feynman"""
    note = get_object_or_404(FeynmanNote, id=note_id, user=request.user)

    if request.method == 'POST':
        # Tạo quiz mới
        quiz = Quiz.objects.create(
            user=request.user,
            title=f"Quiz từ {note.title}",
            description=f"Tạo tự động từ ghi chú Feynman: {note.title}",
            time_limit=10,  # 10 phút
            pass_percentage=70  # 70%
        )

        # Tạo câu hỏi về khái niệm
        question1 = Question.objects.create(
            quiz=quiz,
            text=f"{note.title} là gì?",
            order=1
        )

        # Tạo câu trả lời đúng
        Answer.objects.create(
            question=question1,
            text=note.concept,
            is_correct=True
        )

        # Tạo các câu trả lời sai (giả định)
        Answer.objects.create(
            question=question1,
            text=f"Không phải là {note.title}",
            is_correct=False
        )

        Answer.objects.create(
            question=question1,
            text=f"Một khái niệm khác hoàn toàn",
            is_correct=False
        )

        # Tạo câu hỏi về giải thích
        question2 = Question.objects.create(
            quiz=quiz,
            text=f"Làm thế nào để giải thích {note.title} bằng ngôn ngữ đơn giản?",
            order=2
        )

        # Tạo câu trả lời đúng
        Answer.objects.create(
            question=question2,
            text=note.explanation,
            is_correct=True
        )

        # Tạo các câu trả lời sai (giả định)
        Answer.objects.create(
            question=question2,
            text=f"Giải thích sai về {note.title}",
            is_correct=False
        )

        Answer.objects.create(
            question=question2,
            text=f"Không liên quan đến {note.title}",
            is_correct=False
        )

        # Tạo câu hỏi về lỗ hổng kiến thức nếu có
        if note.gaps_identified:
            question3 = Question.objects.create(
                quiz=quiz,
                text=f"Lỗ hổng kiến thức thường gặp khi học về {note.title} là gì?",
                order=3
            )

            # Tạo câu trả lời đúng
            Answer.objects.create(
                question=question3,
                text=note.gaps_identified,
                is_correct=True
            )

            # Tạo các câu trả lời sai (giả định)
            Answer.objects.create(
                question=question3,
                text=f"Không có lỗ hổng kiến thức nào",
                is_correct=False
            )

            Answer.objects.create(
                question=question3,
                text=f"Lỗ hổng không liên quan",
                is_correct=False
            )

        messages.success(request, f'Đã tạo quiz với {quiz.questions.count()} câu hỏi từ ghi chú Feynman!')
        return redirect('quizzes:quiz_detail', quiz_id=quiz.id)

    context = {
        'note': note
    }

    return render(request, 'advanced_learning/feynman_notes/create_quiz.html', context)

@login_required
def feynman_note_create_mindmap(request, note_id):
    """Tạo sơ đồ tư duy từ ghi chú Feynman"""
    note = get_object_or_404(FeynmanNote, id=note_id, user=request.user)

    if request.method == 'POST':
        # Tạo sơ đồ tư duy mới
        mind_map = MindMap.objects.create(
            user=request.user,
            title=f"Sơ đồ tư duy từ {note.title}",
            subject=note.subject,
            central_topic=note.title
        )

        # Tạo cấu trúc dữ liệu cho sơ đồ tư duy
        map_data = {
            'id': 'root',
            'topic': note.title,
            'children': [
                {
                    'id': 'concept',
                    'topic': 'Khái niệm',
                    'direction': 'right',
                    'children': [{'id': 'concept_detail', 'topic': note.concept}]
                },
                {
                    'id': 'explanation',
                    'topic': 'Giải thích đơn giản',
                    'direction': 'right',
                    'children': [{'id': 'explanation_detail', 'topic': note.explanation[:100] + '...'}]
                }
            ]
        }

        # Thêm lỗ hổng kiến thức nếu có
        if note.gaps_identified:
            map_data['children'].append({
                'id': 'gaps',
                'topic': 'Lỗ hổng kiến thức',
                'direction': 'left',
                'children': [{'id': 'gaps_detail', 'topic': note.gaps_identified[:100] + '...'}]
            })

        # Thêm giải thích đã cải thiện nếu có
        if note.refined_explanation:
            map_data['children'].append({
                'id': 'refined',
                'topic': 'Giải thích nâng cao',
                'direction': 'left',
                'children': [{'id': 'refined_detail', 'topic': note.refined_explanation[:100] + '...'}]
            })

        # Lưu dữ liệu sơ đồ tư duy
        mind_map.map_data = map_data
        mind_map.save()

        messages.success(request, 'Sơ đồ tư duy đã được tạo thành công từ ghi chú Feynman!')
        return redirect('advanced_learning:mind_map_detail', map_id=mind_map.id)

    context = {
        'note': note
    }

    return render(request, 'advanced_learning/feynman_notes/create_mindmap.html', context)

# Hệ thống học tập dựa trên dự án Views
@login_required
def project_list(request):
    """Hiển thị danh sách dự án học tập"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    difficulty = request.GET.get('difficulty', '')
    format_type = request.GET.get('format', '')

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

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/projects/list_partial.html', context)

    return render(request, 'advanced_learning/projects/list.html', context)

@login_required
def project_detail(request, project_id):
    """Chi tiết dự án học tập"""
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all().order_by('order')
    format_type = request.GET.get('format', '')

    # Kiểm tra xem người dùng đã tham gia dự án này chưa
    user_project = UserProject.objects.filter(user=request.user, project=project).first()

    context = {
        'project': project,
        'tasks': tasks,
        'user_project': user_project,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/projects/detail_partial.html', context)

    return render(request, 'advanced_learning/projects/detail.html', context)

@login_required
def create_mindmap_from_project(request, project_id):
    """Tạo Mind Map từ dự án học tập"""
    project = get_object_or_404(Project, id=project_id)
    user_project = get_object_or_404(UserProject, project=project, user=request.user)

    if request.method == 'POST':
        form = MindMapForm(request.POST)
        if form.is_valid():
            # Tạo mind map mới
            mind_map = form.save(commit=False)
            mind_map.user = request.user
            mind_map.subject = project.subject
            mind_map.topic = project.topic
            mind_map.lesson = project.lesson
            mind_map.source_type = 'project'
            mind_map.source_id = project.id

            # Tạo cấu trúc dữ liệu cho mind map từ dự án
            central_topic = project.title
            map_data = {
                'id': 'root',
                'text': central_topic,
                'children': []
            }

            # Thêm các task của dự án vào mind map
            tasks = project.tasks.all().order_by('order')
            for i, task in enumerate(tasks):
                task_node = {
                    'id': f'task-{task.id}',
                    'text': task.title,
                    'children': []
                }

                # Thêm mô tả task nếu có
                if task.description:
                    task_node['children'].append({
                        'id': f'task-{task.id}-desc',
                        'text': task.description[:50] + '...' if len(task.description) > 50 else task.description
                    })

                # Thêm trạng thái task
                status_text = 'Hoàn thành' if user_project.is_task_completed(task.id) else 'Chưa hoàn thành'
                task_node['children'].append({
                    'id': f'task-{task.id}-status',
                    'text': f'Trạng thái: {status_text}'
                })

                map_data['children'].append(task_node)

            # Lưu dữ liệu mind map
            mind_map.central_topic = central_topic
            mind_map.map_data = map_data
            mind_map.save()

            messages.success(request, 'Mind Map đã được tạo thành công từ dự án!')
            return redirect('advanced_learning:mind_map_detail', map_id=mind_map.id)
    else:
        # Tạo form với dữ liệu ban đầu từ dự án
        initial_data = {
            'title': f"Mind Map từ dự án: {project.title}",
            'description': project.description,
        }
        form = MindMapForm(initial=initial_data)

    context = {
        'form': form,
        'project': project,
        'user_project': user_project,
        'is_create': True,
        'from_project': True,
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
    format_type = request.GET.get('format', '')

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

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/projects/my_projects_partial.html', context)

    return render(request, 'advanced_learning/projects/my_projects.html', context)

# Tính năng mới cho hệ thống học tập dựa trên dự án
@login_required
def upload_project_result(request, project_id):
    """Tải lên kết quả dự án"""
    user_project = get_object_or_404(UserProject, project_id=project_id, user=request.user)
    project = user_project.project

    if request.method == 'POST':
        # Xử lý tải lên file
        if 'result_file' in request.FILES:
            result_file = request.FILES['result_file']
            file_name = result_file.name
            file_type = file_name.split('.')[-1].lower()
            description = request.POST.get('description', '')

            # Lưu file vào media
            file_path = f'project_results/{user_project.id}/{file_name}'
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(file_path, result_file)
            file_url = fs.url(filename)

            # Thêm thông tin file vào dự án
            user_project.add_result_file(file_name, file_url, file_type, description)

            messages.success(request, 'Tải lên kết quả dự án thành công!')
            return redirect('advanced_learning:project_detail', project_id=project.id)

    context = {
        'user_project': user_project,
        'project': project
    }

    return render(request, 'advanced_learning/projects/upload_result.html', context)

@login_required
def add_project_comment(request, project_id):
    """Thêm bình luận và đánh giá dự án"""
    user_project = get_object_or_404(UserProject, project_id=project_id, user=request.user)

    if request.method == 'POST':
        content = request.POST.get('content', '')
        rating = request.POST.get('rating', 0)

        # Tạo bình luận mới
        comment = ProjectComment.objects.create(
            user_project=user_project,
            author=request.user,
            content=content,
            rating=rating
        )

        # Cập nhật đánh giá trung bình cho dự án
        avg_rating = ProjectComment.objects.filter(user_project=user_project).aggregate(Avg('rating'))['rating__avg'] or 0
        user_project.rating = round(avg_rating)
        user_project.save(update_fields=['rating'])

        messages.success(request, 'Thêm bình luận và đánh giá thành công!')
        return redirect('advanced_learning:project_detail', project_id=project_id)

    context = {
        'user_project': user_project,
        'project': user_project.project
    }

    return render(request, 'advanced_learning/projects/add_comment.html', context)

@login_required
def share_project(request, project_id):
    """Chia sẻ dự án"""
    user_project = get_object_or_404(UserProject, project_id=project_id, user=request.user)

    if request.method == 'POST':
        # Tạo URL chia sẻ nếu chưa có
        if not user_project.share_url:
            user_project.generate_share_url()

        # Đánh dấu dự án là đã chia sẻ
        user_project.is_shared = True
        user_project.save(update_fields=['is_shared'])

        # Gửi email chia sẻ nếu có email
        email = request.POST.get('email')
        if email:
            share_url = request.build_absolute_uri(reverse('advanced_learning:shared_project_view', args=[user_project.share_url]))
            subject = f"{request.user.username} đã chia sẻ dự án với bạn"
            message = f"Xin chào,\n\n{request.user.username} đã chia sẻ dự án '{user_project.project.title}' với bạn.\n\nBạn có thể xem dự án tại: {share_url}\n\nTrân trọng,\nNền Tảng Học Tập"

            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                messages.success(request, f'Đã chia sẻ dự án với {email}.')
            except Exception as e:
                messages.error(request, f'Không thể gửi email: {str(e)}')

        messages.success(request, 'Dự án đã được chia sẻ thành công!')
        return redirect('advanced_learning:project_detail', project_id=project_id)

    context = {
        'user_project': user_project,
        'project': user_project.project,
        'share_url': request.build_absolute_uri(reverse('advanced_learning:shared_project_view', args=[user_project.share_url])) if user_project.share_url else None
    }

    return render(request, 'advanced_learning/projects/share.html', context)

def shared_project_view(request, share_url):
    """Xem dự án được chia sẻ"""
    user_project = get_object_or_404(UserProject, share_url=share_url, is_shared=True)
    project = user_project.project
    tasks = project.tasks.all().order_by('order')

    context = {
        'user_project': user_project,
        'project': project,
        'tasks': tasks,
        'is_shared_view': True
    }

    return render(request, 'advanced_learning/projects/shared_view.html', context)

@login_required
def link_project_flashcards(request, project_id):
    """Liên kết dự án với bộ flashcard"""
    user_project = get_object_or_404(UserProject, project_id=project_id, user=request.user)

    if request.method == 'POST':
        flashcard_set_id = request.POST.get('flashcard_set')
        if flashcard_set_id:
            flashcard_set = get_object_or_404(FlashcardSet, id=flashcard_set_id, user=request.user)
            user_project.add_flashcard_set(flashcard_set)
            messages.success(request, f'Liên kết thành công với bộ flashcard "{flashcard_set.title}"!')
            return redirect('advanced_learning:project_detail', project_id=project_id)

    # Lấy danh sách các bộ flashcard của người dùng
    flashcard_sets = FlashcardSet.objects.filter(user=request.user)

    context = {
        'user_project': user_project,
        'project': user_project.project,
        'flashcard_sets': flashcard_sets,
        'linked_flashcard_sets': user_project.flashcard_sets.all()
    }

    return render(request, 'advanced_learning/projects/link_flashcards.html', context)

@login_required
def link_project_quiz(request, project_id):
    """Liên kết dự án với quiz"""
    user_project = get_object_or_404(UserProject, project_id=project_id, user=request.user)

    if request.method == 'POST':
        quiz_id = request.POST.get('quiz')
        if quiz_id:
            quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
            user_project.add_quiz(quiz)
            messages.success(request, f'Liên kết thành công với quiz "{quiz.title}"!')
            return redirect('advanced_learning:project_detail', project_id=project_id)

    # Lấy danh sách các quiz của người dùng
    quizzes = Quiz.objects.filter(user=request.user)

    context = {
        'user_project': user_project,
        'project': user_project.project,
        'quizzes': quizzes,
        'linked_quizzes': user_project.quizzes.all()
    }

    return render(request, 'advanced_learning/projects/link_quiz.html', context)

@login_required
def link_project_pomodoro(request, project_id):
    """Liên kết dự án với phiên Pomodoro"""
    user_project = get_object_or_404(UserProject, project_id=project_id, user=request.user)

    if request.method == 'POST':
        # Tạo phiên Pomodoro mới
        duration = int(request.POST.get('duration', 25))
        description = f"Làm việc trên dự án: {user_project.project.title}"

        pomodoro_session = PomodoroSession.objects.create(
            user=request.user,
            duration=duration,
            description=description,
            status='created'
        )

        # Liên kết phiên Pomodoro với dự án
        user_project.add_pomodoro_session(pomodoro_session)

        messages.success(request, f'Đã tạo và liên kết phiên Pomodoro ({duration} phút) với dự án!')
        return redirect('pomodoro:start_session', session_id=pomodoro_session.id)

    context = {
        'user_project': user_project,
        'project': user_project.project,
        'pomodoro_sessions': user_project.pomodoro_sessions.all().order_by('-created_at')
    }

    return render(request, 'advanced_learning/projects/link_pomodoro.html', context)

# Bài tập thực hành tương tác Views
@login_required
def exercise_list(request):
    """Hiển thị danh sách bài tập thực hành tương tác"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    exercise_type = request.GET.get('type', '')
    format_type = request.GET.get('format', '')

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

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/exercises/list_partial.html', context)

    return render(request, 'advanced_learning/exercises/list.html', context)

@login_required
def exercise_detail(request, exercise_id):
    """Chi tiết bài tập thực hành tương tác"""
    exercise = get_object_or_404(InteractiveExercise, id=exercise_id)
    format_type = request.GET.get('format', '')

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

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/exercises/detail_partial.html', context)

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

# Tính năng mới cho bài tập thực hành tương tác
@login_required
@require_POST
def run_code(request, exercise_id):
    """Chạy mã và kiểm tra kết quả"""
    exercise = get_object_or_404(InteractiveExercise, id=exercise_id)

    # Kiểm tra xem bài tập có phải loại lập trình không
    if exercise.exercise_type != 'code':
        return JsonResponse({
            'success': False,
            'error': 'Bài tập này không phải là bài tập lập trình'
        })

    # Lấy mã nguồn từ request
    code = request.POST.get('code', '')
    if not code:
        return JsonResponse({
            'success': False,
            'error': 'Không có mã nguồn được cung cấp'
        })

    # Thời gian bắt đầu thực thi
    start_time = time.time()

    # Thực thi mã và kiểm tra kết quả
    execution_result = {}
    is_correct = False
    feedback = ''

    try:
        # Xử lý thực thi mã tùy theo ngôn ngữ lập trình
        if exercise.programming_language == 'python':
            # Thực thi mã Python an toàn
            execution_result = execute_python_code(code, exercise.test_cases)
        elif exercise.programming_language == 'javascript':
            # Thực thi mã JavaScript
            execution_result = {'output': 'JavaScript execution not implemented yet'}
        else:
            execution_result = {'output': f'Ngôn ngữ {exercise.programming_language} chưa được hỗ trợ'}

        # Kiểm tra kết quả với các trường hợp kiểm tra
        if 'test_results' in execution_result:
            # Đếm số trường hợp kiểm tra đã vượt qua
            passed_tests = sum(1 for test in execution_result['test_results'] if test.get('passed', False))
            total_tests = len(execution_result['test_results'])

            if passed_tests == total_tests and total_tests > 0:
                is_correct = True
                feedback = f'Chúc mừng! Bạn đã vượt qua tất cả {total_tests} trường hợp kiểm tra.'
            else:
                feedback = f'Bạn đã vượt qua {passed_tests}/{total_tests} trường hợp kiểm tra. Hãy tiếp tục cố gắng!'
        else:
            feedback = 'Mã của bạn đã được thực thi, nhưng không có trường hợp kiểm tra nào được định nghĩa.'

    except Exception as e:
        execution_result = {'error': str(e)}
        feedback = f'Lỗi khi thực thi mã: {str(e)}'

    # Thời gian kết thúc thực thi
    end_time = time.time()
    execution_time = end_time - start_time

    # Lưu kết quả nộp bài
    submission = ExerciseSubmission.objects.create(
        user=request.user,
        exercise=exercise,
        submission_content=code,
        is_correct=is_correct,
        feedback=feedback,
        execution_time=execution_time,
        execution_result=execution_result
    )

    # Tính toán điểm nếu đúng
    points_earned = 0
    if is_correct:
        points_earned = submission.calculate_points()

        # Kiểm tra và cấp thành tích nếu có
        check_and_award_achievements(request.user, exercise)

    # Trả về kết quả
    return JsonResponse({
        'success': True,
        'is_correct': is_correct,
        'feedback': feedback,
        'execution_result': execution_result,
        'execution_time': f'{execution_time:.3f}s',
        'points_earned': points_earned,
        'solution': exercise.solution if is_correct else None
    })

@login_required
@require_POST
def get_exercise_hint(request, exercise_id):
    """Lấy gợi ý cho bài tập"""
    exercise = get_object_or_404(InteractiveExercise, id=exercise_id)

    # Lấy chỉ số gợi ý
    hint_index = int(request.POST.get('hint_index', 0))

    # Kiểm tra xem có gợi ý không
    if not exercise.hints or hint_index >= len(exercise.hints):
        return JsonResponse({
            'success': False,
            'error': 'Không có gợi ý nào cho bài tập này hoặc chỉ số gợi ý không hợp lệ'
        })

    # Lấy gợi ý
    hint = exercise.hints[hint_index]

    # Lưu gợi ý đã sử dụng
    # Tìm kiếm bài nộp gần nhất của người dùng
    submission = ExerciseSubmission.objects.filter(user=request.user, exercise=exercise).order_by('-created_at').first()

    if submission:
        # Cập nhật danh sách gợi ý đã sử dụng
        hints_used = submission.hints_used or []
        if hint not in hints_used:
            hints_used.append(hint)
            submission.hints_used = hints_used
            submission.save(update_fields=['hints_used'])
    else:
        # Tạo bài nộp mới với gợi ý đã sử dụng
        submission = ExerciseSubmission.objects.create(
            user=request.user,
            exercise=exercise,
            submission_content='',
            hints_used=[hint]
        )

    # Trả về gợi ý
    return JsonResponse({
        'success': True,
        'hint': hint.get('content', ''),
        'cost': hint.get('cost', 0),
        'hint_index': hint_index,
        'total_hints': len(exercise.hints)
    })

@login_required
def exercise_submissions(request, exercise_id):
    """Xem các bài nộp của bài tập"""
    exercise = get_object_or_404(InteractiveExercise, id=exercise_id)

    # Lấy các bài nộp của người dùng cho bài tập này
    submissions = ExerciseSubmission.objects.filter(user=request.user, exercise=exercise).order_by('-created_at')

    context = {
        'exercise': exercise,
        'submissions': submissions
    }

    return render(request, 'advanced_learning/exercises/submissions.html', context)

@login_required
def my_exercise_submissions(request):
    """Xem tất cả các bài nộp của người dùng"""
    # Tìm kiếm và lọc
    exercise_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    format_type = request.GET.get('format', '')

    # Lấy các bài nộp của người dùng
    submissions = ExerciseSubmission.objects.filter(user=request.user).order_by('-created_at')

    # Áp dụng bộ lọc
    if exercise_type:
        submissions = submissions.filter(exercise__exercise_type=exercise_type)

    if status:
        if status == 'correct':
            submissions = submissions.filter(is_correct=True)
        elif status == 'incorrect':
            submissions = submissions.filter(is_correct=False)

    # Phân trang
    paginator = Paginator(submissions, 10)
    page = request.GET.get('page')
    try:
        submissions_page = paginator.page(page)
    except PageNotAnInteger:
        submissions_page = paginator.page(1)
    except EmptyPage:
        submissions_page = paginator.page(paginator.num_pages)

    # Tính toán thống kê
    total_submissions = submissions.count()
    correct_submissions = submissions.filter(is_correct=True).count()
    total_points = submissions.filter(is_correct=True).aggregate(Sum('points'))['points__sum'] or 0
    completion_rate = int(correct_submissions / total_submissions * 100) if total_submissions > 0 else 0

    context = {
        'submissions': submissions_page,
        'exercise_types': InteractiveExercise.EXERCISE_TYPES,
        'selected_type': exercise_type,
        'selected_status': status,
        'total_submissions': total_submissions,
        'correct_submissions': correct_submissions,
        'total_points': total_points,
        'completion_rate': completion_rate
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/exercises/my_submissions_partial.html', context)

    return render(request, 'advanced_learning/exercises/my_submissions.html', context)

@login_required
def exercise_leaderboard(request):
    """Bảng xếp hạng bài tập"""
    # Tìm kiếm và lọc
    exercise_type = request.GET.get('type', '')
    time_period = request.GET.get('period', 'all')

    # Tính toán thời gian bắt đầu dựa trên khoảng thời gian
    start_date = None
    if time_period == 'day':
        start_date = timezone.now() - timedelta(days=1)
    elif time_period == 'week':
        start_date = timezone.now() - timedelta(weeks=1)
    elif time_period == 'month':
        start_date = timezone.now() - timedelta(days=30)

    # Lấy các bài nộp đúng
    submissions = ExerciseSubmission.objects.filter(is_correct=True)

    # Áp dụng bộ lọc
    if exercise_type:
        submissions = submissions.filter(exercise__exercise_type=exercise_type)

    if start_date:
        submissions = submissions.filter(created_at__gte=start_date)

    # Tính toán điểm cho mỗi người dùng
    user_points = submissions.values('user').annotate(
        total_points=Sum('points_earned'),
        correct_submissions=Count('id')
    ).order_by('-total_points')

    # Lấy thông tin người dùng
    for entry in user_points:
        user = User.objects.get(id=entry['user'])
        entry['username'] = user.username
        entry['full_name'] = f"{user.first_name} {user.last_name}".strip() or user.username

    context = {
        'user_points': user_points,
        'exercise_types': InteractiveExercise.EXERCISE_TYPES,
        'selected_type': exercise_type,
        'selected_period': time_period
    }

    return render(request, 'advanced_learning/exercises/leaderboard.html', context)

@login_required
def link_exercise_achievement(request, exercise_id):
    """Liên kết bài tập với thành tích"""
    exercise = get_object_or_404(InteractiveExercise, id=exercise_id)

    if request.method == 'POST':
        achievement_id = request.POST.get('achievement')
        if achievement_id:
            achievement = get_object_or_404(Achievement, id=achievement_id)
            exercise.achievements.add(achievement)
            messages.success(request, f'Liên kết thành công với thành tích "{achievement.title}"!')
            return redirect('advanced_learning:exercise_detail', exercise_id=exercise_id)

    # Lấy danh sách các thành tích
    achievements = Achievement.objects.filter(achievement_type='exercise')

    context = {
        'exercise': exercise,
        'achievements': achievements,
        'linked_achievements': exercise.achievements.all()
    }

    return render(request, 'advanced_learning/exercises/link_achievement.html', context)

# Hàm hỗ trợ
def execute_python_code(code, test_cases):
    """Thực thi mã Python an toàn và kiểm tra với các trường hợp kiểm tra"""
    result = {'output': '', 'test_results': []}

    # Tạo môi trường thực thi an toàn
    restricted_globals = {
        '__builtins__': {
            'print': print,
            'len': len,
            'range': range,
            'int': int,
            'float': float,
            'str': str,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'sum': sum,
            'min': min,
            'max': max,
            'abs': abs,
            'round': round,
            'sorted': sorted,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'any': any,
            'all': all,
            'bool': bool,
            'type': type,
            'Exception': Exception,
            'ValueError': ValueError,
            'TypeError': TypeError,
            'IndexError': IndexError,
            'KeyError': KeyError,
        }
    }

    # Thực thi mã
    try:
        # Chuyển hướng output
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        # Biên dịch mã
        compiled_code = compile(code, '<string>', 'exec')

        # Thực thi mã
        exec(compiled_code, restricted_globals)

        # Lấy output
        result['output'] = redirected_output.getvalue()

        # Kiểm tra với các trường hợp kiểm tra
        if test_cases:
            for test_case in test_cases:
                test_result = {'input': test_case.get('input', ''), 'passed': False}

                # Thực thi test case
                try:
                    # Chuẩn bị input
                    test_input = test_case.get('input', '')

                    # Thực thi hàm với input
                    if 'function_name' in test_case:
                        func_name = test_case['function_name']
                        if func_name in restricted_globals:
                            # Chuyển đổi input thành các tham số
                            args = eval(test_input, {'__builtins__': restricted_globals['__builtins__']})
                            output = restricted_globals[func_name](*args)
                        else:
                            output = f"Hàm '{func_name}' không được định nghĩa"
                    else:
                        # Thực thi mã với input
                        test_globals = restricted_globals.copy()
                        test_globals['input_value'] = test_input
                        test_code = f"result = {test_input}"
                        exec(test_code, test_globals)
                        output = test_globals.get('result', None)

                    # So sánh với kết quả mong đợi
                    expected_output = test_case.get('expected_output', '')

                    # Chuyển đổi kết quả mong đợi thành giá trị Python nếu có thể
                    try:
                        expected_value = eval(expected_output, {'__builtins__': restricted_globals['__builtins__']})
                    except:
                        expected_value = expected_output

                    # Kiểm tra kết quả
                    test_result['expected'] = str(expected_value)
                    test_result['actual'] = str(output)
                    test_result['passed'] = output == expected_value

                except Exception as e:
                    test_result['error'] = str(e)

                # Thêm kết quả test case
                result['test_results'].append(test_result)

    except Exception as e:
        result['error'] = str(e)

    finally:
        # Khôi phục stdout
        sys.stdout = old_stdout

    return result

def check_and_award_achievements(user, exercise):
    """Kiểm tra và cấp thành tích cho người dùng"""
    # Lấy các thành tích liên quan đến bài tập
    exercise_achievements = exercise.achievements.all()

    for achievement in exercise_achievements:
        # Kiểm tra xem người dùng đã có thành tích này chưa
        if not UserAchievement.objects.filter(user=user, achievement=achievement).exists():
            # Cấp thành tích mới
            user_achievement = UserAchievement.objects.create(
                user=user,
                achievement=achievement
            )

            # Tạo thông báo
            Notification.objects.create(
                user=user,
                title=f'Đã đạt được thành tích: {achievement.title}',
                message=f'Chúc mừng! Bạn đã đạt được thành tích "{achievement.title}". {achievement.description}',
                notification_type='success',
                related_feature='exercise',
                related_object_id=exercise.id,
                url=reverse('advanced_learning:exercise_detail', args=[exercise.id])
            )

# Chế độ thi đấu Views
@login_required
def competition_list(request):
    """Hiển thị danh sách các cuộc thi đấu"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    status = request.GET.get('status', '')
    difficulty = request.GET.get('difficulty', '')
    competition_type = request.GET.get('type', '')
    lesson_id = request.GET.get('lesson', '')
    format_type = request.GET.get('format', '')
    view = request.GET.get('view', 'list')
    tab = request.GET.get('tab', '')

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

        # Nếu chọn chủ đề, lấy danh sách bài học cho chủ đề đó
        lessons = Lesson.objects.filter(topic__subject_id=subject_id).order_by('topic__order', 'order')
    else:
        lessons = Lesson.objects.none()

    if lesson_id:
        competitions = competitions.filter(lesson_id=lesson_id)

    if difficulty:
        competitions = competitions.filter(difficulty_level=difficulty)

    if competition_type:
        competitions = competitions.filter(competition_type=competition_type)

    if status:
        now = timezone.now()
        if status == 'upcoming':
            competitions = competitions.filter(start_time__gt=now)
        elif status == 'active':
            competitions = competitions.filter(start_time__lte=now, end_time__gte=now, is_active=True)
        elif status == 'past':
            competitions = competitions.filter(end_time__lt=now)
        elif status == 'featured':
            competitions = competitions.filter(is_featured=True)

    # Lấy danh sách các chủ đề cho bộ lọc
    subjects = Subject.objects.all()

    # Lấy danh sách các cuộc thi mà người dùng đã tham gia
    user_competitions = CompetitionParticipant.objects.filter(user=request.user).values_list('competition_id', flat=True)

    # Lấy danh sách các cuộc thi nổi bật
    featured_competitions = CompetitionMode.objects.filter(is_featured=True, is_active=True).order_by('-start_time')[:5]

    # Lấy danh sách các cuộc thi sắp diễn ra
    now = timezone.now()
    upcoming_competitions = CompetitionMode.objects.filter(start_time__gt=now, is_active=True).order_by('start_time')[:5]

    # Lấy danh sách các cuộc thi đang diễn ra
    active_competitions = CompetitionMode.objects.filter(start_time__lte=now, end_time__gte=now, is_active=True).order_by('end_time')[:5]

    # Kiểm tra xem người dùng có đăng ký nhận thông báo không
    has_subscription = CompetitionSubscription.objects.filter(user=request.user, notification_type='all').exists()

    context = {
        'competitions': competitions,
        'subjects': subjects,
        'lessons': lessons,
        'search_query': search_query,
        'selected_subject': subject_id,
        'selected_lesson': lesson_id,
        'selected_status': status,
        'selected_difficulty': difficulty,
        'selected_type': competition_type,
        'user_competitions': user_competitions,
        'featured_competitions': featured_competitions,
        'upcoming_competitions': upcoming_competitions,
        'active_competitions': active_competitions,
        'has_subscription': has_subscription,
        'difficulty_levels': CompetitionMode.DIFFICULTY_LEVELS,
        'competition_types': CompetitionMode.COMPETITION_TYPES,
        'view': view,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/competitions/list_partial.html', context)

    return render(request, 'advanced_learning/competitions/list.html', context)

@login_required
def competition_detail(request, competition_id):
    """Chi tiết cuộc thi đấu"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)
    format_type = request.GET.get('format', '')

    # Kiểm tra xem người dùng đã tham gia cuộc thi này chưa
    user_participant = CompetitionParticipant.objects.filter(user=request.user, competition=competition).first()

    # Lấy danh sách câu hỏi
    questions = CompetitionQuestion.objects.filter(competition=competition).order_by('order')

    # Lấy danh sách người tham gia
    participants = CompetitionParticipant.objects.filter(competition=competition).order_by('-score')

    # Lấy số người tham gia
    participant_count = participants.count()

    # Lấy trạng thái hiện tại của cuộc thi
    now = timezone.now()
    is_active = competition.is_active and competition.start_time <= now and competition.end_time >= now

    context = {
        'competition': competition,
        'user_participant': user_participant,
        'questions': questions,
        'participants': participants,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/competitions/detail_partial.html', context)

    return render(request, 'advanced_learning/competitions/detail.html', context)

@login_required
def competition_leaderboard(request, competition_id):
    """Bảng xếp hạng cuộc thi"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)
    format_type = request.GET.get('format', '')

    # Lấy bảng xếp hạng
    participants = CompetitionParticipant.objects.filter(competition=competition).order_by('-score', 'end_time')

    context = {
        'competition': competition,
        'participants': participants,
    }

    return render(request, 'advanced_learning/competitions/leaderboard_partial.html', context)

@login_required
def competition_participants(request, competition_id):
    """Danh sách người tham gia cuộc thi"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)
    format_type = request.GET.get('format', '')

    # Lấy danh sách người tham gia
    participants = CompetitionParticipant.objects.filter(competition=competition).order_by('-joined_at')

    context = {
        'competition': competition,
        'participants': participants,
    }

    return render(request, 'advanced_learning/competitions/participants_partial.html', context)

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
def competition_leaderboard(request, competition_id):
    """Bảng xếp hạng cuộc thi"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)
    format_type = request.GET.get('format', '')

    # Lấy bảng xếp hạng
    participants = CompetitionParticipant.objects.filter(competition=competition).order_by('-score', 'end_time')

    context = {
        'competition': competition,
        'participants': participants,
    }

    return render(request, 'advanced_learning/competitions/leaderboard_partial.html', context)

@login_required
def competition_participants(request, competition_id):
    """Danh sách người tham gia cuộc thi"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)
    format_type = request.GET.get('format', '')

    # Lấy danh sách người tham gia
    participants = CompetitionParticipant.objects.filter(competition=competition).order_by('-joined_at')

    context = {
        'competition': competition,
        'participants': participants,
    }

    return render(request, 'advanced_learning/competitions/participants_partial.html', context)

@login_required
def my_competitions(request):
    """Danh sách các cuộc thi đã tham gia"""
    # Tìm kiếm và lọc
    status = request.GET.get('status', '')
    competition_type = request.GET.get('type', '')
    format_type = request.GET.get('format', '')

    # Lấy danh sách các cuộc thi đã tham gia
    participations = CompetitionParticipant.objects.filter(user=request.user).order_by('-start_time')

    # Áp dụng bộ lọc
    if status:
        if status == 'completed':
            participations = participations.filter(end_time__isnull=False)
        elif status == 'in_progress':
            participations = participations.filter(end_time__isnull=True)

    if competition_type:
        participations = participations.filter(competition__competition_type=competition_type)

    # Tính điểm cao nhất
    highest_score = participations.filter(end_time__isnull=False).order_by('-score').values_list('score', flat=True).first() or 0

    # Tím xếp hạng cao nhất (số nhỏ nhất)
    best_rank = participations.filter(rank__isnull=False).order_by('rank').values_list('rank', flat=True).first()

    # Lấy danh sách các nhóm của người dùng
    user_teams = CompetitionTeam.objects.filter(leader=request.user).order_by('-created_at')

    # Lấy danh sách các cuộc thi trực tiếp của người dùng
    live_participations = LiveParticipant.objects.filter(user=request.user).order_by('-joined_at')

    # Lấy tổng điểm đã kiếm được từ các cuộc thi
    total_points = participations.filter(end_time__isnull=False).aggregate(total=Sum('score'))['total'] or 0

    # Lấy danh sách các thành tích đã đạt được
    user_achievements = UserAchievement.objects.filter(
        user=request.user,
        achievement__achievement_type='competition'
    ).order_by('-earned_at')

    context = {
        'participations': participations,
        'highest_score': highest_score,
        'best_rank': best_rank,
        'user_teams': user_teams,
        'live_participations': live_participations,
        'total_points': total_points,
        'user_achievements': user_achievements,
        'selected_status': status,
        'selected_type': competition_type,
        'competition_types': CompetitionMode.COMPETITION_TYPES,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'advanced_learning/competitions/my_competitions_partial.html', context)

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

    # Tạo dữ liệu cho biểu đồ so sánh việc sử dụng các tính năng học tập nâng cao
    feature_comparison = {
        'labels': list(feature_usage.keys()),
        'values': list(feature_usage.values()),
        'colors': [
            'rgba(220, 53, 69, 0.7)',   # Pomodoro - Đỏ
            'rgba(13, 110, 253, 0.7)',   # Cornell Notes - Xanh dương
            'rgba(25, 135, 84, 0.7)',     # Mind Maps - Xanh lá
            'rgba(255, 193, 7, 0.7)',     # Feynman Notes - Vàng
            'rgba(23, 162, 184, 0.7)',    # Projects - Xanh ngọc
            'rgba(253, 126, 20, 0.7)',    # Competitions - Cam
        ]
    }

    # Tạo dữ liệu cho biểu đồ tiến độ dự án theo thời gian
    # Lấy dữ liệu tiến độ dự án trong 30 ngày qua
    user_projects = UserProject.objects.filter(user=request.user, updated_at__gte=last_30_days)

    # Tạo từ điển để lưu trữ tiến độ trung bình theo ngày
    project_progress_data = {}
    for i in range(30):
        date = (now - timedelta(days=i)).date()
        project_progress_data[date] = {'total': 0, 'count': 0}

    # Tính tiến độ trung bình cho mỗi ngày
    for project in user_projects:
        # Lấy lịch sử tiến độ nếu có
        progress_history = project.progress_history or {}

        # Nếu không có lịch sử, sử dụng tiến độ hiện tại
        if not progress_history:
            date = project.updated_at.date()
            if date in project_progress_data:
                project_progress_data[date]['total'] += project.progress
                project_progress_data[date]['count'] += 1
        else:
            # Xử lý lịch sử tiến độ
            for date_str, progress in progress_history.items():
                try:
                    date = timezone.datetime.fromisoformat(date_str).date()
                    if date in project_progress_data:
                        project_progress_data[date]['total'] += progress
                        project_progress_data[date]['count'] += 1
                except (ValueError, TypeError):
                    continue

    # Tính tiến độ trung bình cho mỗi ngày
    for date in project_progress_data:
        if project_progress_data[date]['count'] > 0:
            project_progress_data[date] = project_progress_data[date]['total'] / project_progress_data[date]['count']
        else:
            project_progress_data[date] = 0

    # Chuyển đổi dữ liệu cho biểu đồ
    project_progress_labels = [date.strftime('%d/%m') for date in sorted(project_progress_data.keys())]
    project_progress_values = [project_progress_data[date] for date in sorted(project_progress_data.keys())]

    # Tạo dữ liệu cho biểu đồ điểm thi đấu theo thời gian
    # Lấy dữ liệu điểm thi đấu trong 30 ngày qua
    competition_participants = CompetitionParticipant.objects.filter(
        user=request.user,
        end_time__isnull=False,
        end_time__gte=last_30_days
    ).order_by('end_time')

    # Tạo từ điển để lưu trữ điểm thi đấu theo ngày
    competition_points_data = {}
    for i in range(30):
        date = (now - timedelta(days=i)).date()
        competition_points_data[date] = 0

    # Tính tổng điểm cho mỗi ngày
    for participant in competition_participants:
        date = participant.end_time.date()
        if date in competition_points_data:
            competition_points_data[date] += participant.score

    # Chuyển đổi dữ liệu cho biểu đồ
    competition_points_labels = [date.strftime('%d/%m') for date in sorted(competition_points_data.keys())]
    competition_points_values = [competition_points_data[date] for date in sorted(competition_points_data.keys())]

    # Tính tổng điểm tích lũy theo thời gian
    competition_points_cumulative = []
    cumulative_sum = 0
    for points in competition_points_values:
        cumulative_sum += points
        competition_points_cumulative.append(cumulative_sum)

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

    # Lấy xếp hạng tốt nhất trong các cuộc thi
    best_rank = CompetitionParticipant.objects.filter(
        user=request.user,
        rank__isnull=False
    ).order_by('rank').first()

    context = {
        'pomodoro_labels': pomodoro_labels,
        'pomodoro_values': pomodoro_values,
        'feature_usage': feature_usage,
        'feature_comparison': feature_comparison,
        'project_progress_labels': project_progress_labels,
        'project_progress_values': project_progress_values,
        'competition_points_labels': competition_points_labels,
        'competition_points_values': competition_points_values,
        'competition_points_cumulative': competition_points_cumulative,
        'total_study_minutes': total_study_minutes,
        'total_competition_points': total_competition_points,
        'avg_project_progress': avg_project_progress,
        'learning_trends': learning_trends,
        'best_rank': best_rank,
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


# View cho đăng ký nhận thông báo cuộc thi
@login_required
@require_POST
def subscribe_competition_notifications(request):
    """Cho phép người dùng đăng ký nhận thông báo về cuộc thi"""
    notification_type = request.POST.get('notification_type', 'all')
    subject_id = request.POST.get('subject_id')
    competition_id = request.POST.get('competition_id')
    email_notification = request.POST.get('email_notification') == 'on'
    push_notification = request.POST.get('push_notification') == 'on'

    # Kiểm tra xem đã có đăng ký này chưa
    existing_subscription = CompetitionSubscription.objects.filter(
        user=request.user,
        notification_type=notification_type,
        subject_id=subject_id if notification_type == 'subject' else None,
        competition_id=competition_id if notification_type == 'specific' else None
    ).first()

    if existing_subscription:
        # Cập nhật đăng ký hiện tại
        existing_subscription.email_notification = email_notification
        existing_subscription.push_notification = push_notification
        existing_subscription.save()
        messages.success(request, 'Đã cập nhật đăng ký nhận thông báo thành công!')
    else:
        # Tạo đăng ký mới
        CompetitionSubscription.objects.create(
            user=request.user,
            notification_type=notification_type,
            subject_id=subject_id if notification_type == 'subject' else None,
            competition_id=competition_id if notification_type == 'specific' else None,
            email_notification=email_notification,
            push_notification=push_notification
        )
        messages.success(request, 'Đã đăng ký nhận thông báo thành công!')

    # Chuyển hướng về trang trước
    redirect_url = request.POST.get('redirect_url') or reverse('advanced_learning:competition_list')
    return redirect(redirect_url)

@login_required
@require_POST
def unsubscribe_competition_notifications(request):
    """Cho phép người dùng hủy đăng ký nhận thông báo về cuộc thi"""
    subscription_id = request.POST.get('subscription_id')

    if subscription_id:
        # Xóa đăng ký cụ thể
        subscription = get_object_or_404(CompetitionSubscription, id=subscription_id, user=request.user)
        subscription.delete()
        messages.success(request, 'Đã hủy đăng ký nhận thông báo thành công!')
    else:
        # Xóa tất cả đăng ký
        notification_type = request.POST.get('notification_type', 'all')
        subject_id = request.POST.get('subject_id')
        competition_id = request.POST.get('competition_id')

        subscriptions = CompetitionSubscription.objects.filter(user=request.user)

        if notification_type:
            subscriptions = subscriptions.filter(notification_type=notification_type)

        if subject_id and notification_type == 'subject':
            subscriptions = subscriptions.filter(subject_id=subject_id)

        if competition_id and notification_type == 'specific':
            subscriptions = subscriptions.filter(competition_id=competition_id)

        subscriptions.delete()
        messages.success(request, 'Đã hủy đăng ký nhận thông báo thành công!')

    # Chuyển hướng về trang trước
    redirect_url = request.POST.get('redirect_url') or reverse('advanced_learning:competition_list')
    return redirect(redirect_url)

@login_required
def my_competition_subscriptions(request):
    """Hiển thị danh sách các đăng ký nhận thông báo của người dùng"""
    # Lấy danh sách các đăng ký
    subscriptions = CompetitionSubscription.objects.filter(user=request.user).order_by('-created_at')

    # Lấy danh sách các chủ đề
    subjects = Subject.objects.all()

    context = {
        'subscriptions': subscriptions,
        'subjects': subjects,
    }

    return render(request, 'advanced_learning/competitions/my_subscriptions.html', context)


# View cho thi đấu trực tiếp
@login_required
def live_competitions(request):
    """Hiển thị danh sách các cuộc thi trực tiếp"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    status = request.GET.get('status', '')

    # Lấy danh sách các cuộc thi trực tiếp
    live_competitions = LiveCompetition.objects.all().order_by('-start_time')

    # Áp dụng bộ lọc
    if search_query:
        live_competitions = live_competitions.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(competition__title__icontains=search_query)
        )

    if status:
        live_competitions = live_competitions.filter(status=status)

    # Lấy danh sách các cuộc thi trực tiếp mà người dùng đã tham gia
    user_live_competitions = LiveParticipant.objects.filter(user=request.user).values_list('live_competition_id', flat=True)

    context = {
        'live_competitions': live_competitions,
        'search_query': search_query,
        'selected_status': status,
        'user_live_competitions': user_live_competitions,
        'status_choices': LiveCompetition.STATUS_CHOICES,
    }

    return render(request, 'advanced_learning/competitions/live_competitions.html', context)

@login_required
def create_live_competition(request, competition_id=None):
    """Tạo cuộc thi trực tiếp mới"""
    if competition_id:
        competition = get_object_or_404(CompetitionMode, id=competition_id)
    else:
        competition = None

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        max_participants = request.POST.get('max_participants', 20)

        if not title:
            messages.error(request, 'Vui lòng nhập tiêu đề cho cuộc thi trực tiếp!')
            return redirect('advanced_learning:create_live_competition')

        # Tạo cuộc thi trực tiếp mới
        live_competition = LiveCompetition.objects.create(
            host=request.user,
            competition=competition,
            title=title,
            description=description,
            max_participants=max_participants,
            status='waiting'
        )

        # Tự động tham gia với tư cách là người tổ chức
        LiveParticipant.objects.create(
            live_competition=live_competition,
            user=request.user,
            is_active=True
        )

        messages.success(request, 'Cuộc thi trực tiếp đã được tạo thành công!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Lấy danh sách các cuộc thi có thể tạo cuộc thi trực tiếp
    if not competition:
        competitions = CompetitionMode.objects.filter(
            Q(competition_type='live') | Q(competition_type='realtime'),
            is_active=True
        ).order_by('-start_time')
    else:
        competitions = [competition]

    context = {
        'competitions': competitions,
        'selected_competition': competition,
    }

    return render(request, 'advanced_learning/competitions/create_live_competition.html', context)

@login_required
def live_competition_detail(request, live_competition_id):
    """Chi tiết cuộc thi trực tiếp"""
    live_competition = get_object_or_404(LiveCompetition, id=live_competition_id)

    # Kiểm tra xem người dùng đã tham gia cuộc thi này chưa
    user_participation = LiveParticipant.objects.filter(user=request.user, live_competition=live_competition).first()

    # Kiểm tra xem có thể tham gia cuộc thi không
    can_join = not live_competition.is_full() and live_competition.status == 'waiting'

    # Lấy danh sách người tham gia
    participants = LiveParticipant.objects.filter(live_competition=live_competition).order_by('-score')

    # Lấy câu hỏi hiện tại
    current_question = live_competition.get_current_question()

    # Kiểm tra xem người dùng có phải là người tổ chức không
    is_host = live_competition.host == request.user

    context = {
        'live_competition': live_competition,
        'user_participation': user_participation,
        'can_join': can_join,
        'participants': participants,
        'current_question': current_question,
        'is_host': is_host,
    }

    return render(request, 'advanced_learning/competitions/live_competition_detail.html', context)

@login_required
@require_POST
def join_live_competition(request, live_competition_id):
    """Tham gia cuộc thi trực tiếp"""
    live_competition = get_object_or_404(LiveCompetition, id=live_competition_id)

    # Kiểm tra xem người dùng đã tham gia cuộc thi này chưa
    if LiveParticipant.objects.filter(user=request.user, live_competition=live_competition).exists():
        messages.warning(request, 'Bạn đã tham gia cuộc thi này rồi!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Kiểm tra xem cuộc thi có đang chờ bắt đầu không
    if live_competition.status != 'waiting':
        messages.warning(request, 'Cuộc thi này không còn chờ tham gia!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Kiểm tra xem cuộc thi có đầy chưa
    if live_competition.is_full():
        messages.warning(request, 'Cuộc thi này đã đầy!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Tham gia cuộc thi
    LiveParticipant.objects.create(
        live_competition=live_competition,
        user=request.user,
        is_active=True
    )

    messages.success(request, 'Bạn đã tham gia cuộc thi thành công!')
    return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

@login_required
@require_POST
def leave_live_competition(request, live_competition_id):
    """Rời khỏi cuộc thi trực tiếp"""
    live_competition = get_object_or_404(LiveCompetition, id=live_competition_id)

    # Kiểm tra xem người dùng có phải là người tổ chức không
    if live_competition.host == request.user:
        messages.warning(request, 'Người tổ chức không thể rời khỏi cuộc thi!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Kiểm tra xem người dùng đã tham gia cuộc thi này chưa
    participant = LiveParticipant.objects.filter(user=request.user, live_competition=live_competition).first()
    if not participant:
        messages.warning(request, 'Bạn chưa tham gia cuộc thi này!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Kiểm tra xem cuộc thi có đang diễn ra không
    if live_competition.status == 'active':
        # Đánh dấu là không còn hoạt động
        participant.is_active = False
        participant.save(update_fields=['is_active'])
        messages.warning(request, 'Bạn đã rời khỏi cuộc thi đang diễn ra!')
    else:
        # Xóa người tham gia
        participant.delete()
        messages.success(request, 'Bạn đã rời khỏi cuộc thi thành công!')

    return redirect('advanced_learning:live_competitions')

@login_required
@require_POST
def start_live_competition(request, live_competition_id):
    """Bắt đầu cuộc thi trực tiếp"""
    live_competition = get_object_or_404(LiveCompetition, id=live_competition_id)

    # Kiểm tra xem người dùng có phải là người tổ chức không
    if live_competition.host != request.user:
        messages.warning(request, 'Chỉ người tổ chức mới có thể bắt đầu cuộc thi!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Kiểm tra xem cuộc thi có đang chờ bắt đầu không
    if live_competition.status != 'waiting':
        messages.warning(request, 'Cuộc thi này không thể bắt đầu!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Kiểm tra xem có người tham gia không
    if LiveParticipant.objects.filter(live_competition=live_competition).count() <= 1:
        messages.warning(request, 'Cần có ít nhất một người tham gia để bắt đầu cuộc thi!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Bắt đầu cuộc thi
    live_competition.status = 'active'
    live_competition.start_time = timezone.now()
    live_competition.save(update_fields=['status', 'start_time'])

    messages.success(request, 'Cuộc thi đã bắt đầu!')
    return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

@login_required
@require_POST
def next_question(request, live_competition_id):
    """Chuyển sang câu hỏi tiếp theo"""
    live_competition = get_object_or_404(LiveCompetition, id=live_competition_id)

    # Kiểm tra xem người dùng có phải là người tổ chức không
    if live_competition.host != request.user:
        messages.warning(request, 'Chỉ người tổ chức mới có thể chuyển câu hỏi!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Kiểm tra xem cuộc thi có đang diễn ra không
    if live_competition.status != 'active':
        messages.warning(request, 'Cuộc thi không đang diễn ra!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Chuyển sang câu hỏi tiếp theo
    if not live_competition.next_question():
        # Đã hết câu hỏi, kết thúc cuộc thi
        live_competition.status = 'completed'
        live_competition.end_time = timezone.now()
        live_competition.save(update_fields=['status', 'end_time'])
        messages.success(request, 'Cuộc thi đã kết thúc!')
    else:
        messages.success(request, 'Đã chuyển sang câu hỏi tiếp theo!')

    return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

@login_required
@require_POST
def submit_live_answer(request, live_competition_id):
    """Nộp câu trả lời cho cuộc thi trực tiếp"""
    live_competition = get_object_or_404(LiveCompetition, id=live_competition_id)

    # Kiểm tra xem người dùng đã tham gia cuộc thi này chưa
    participant = LiveParticipant.objects.filter(user=request.user, live_competition=live_competition, is_active=True).first()
    if not participant:
        messages.warning(request, 'Bạn không phải là người tham gia hoặc không còn hoạt động trong cuộc thi này!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Kiểm tra xem cuộc thi có đang diễn ra không
    if live_competition.status != 'active':
        messages.warning(request, 'Cuộc thi không đang diễn ra!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Lấy câu hỏi hiện tại
    current_question = live_competition.get_current_question()
    if not current_question:
        messages.warning(request, 'Không có câu hỏi hiện tại!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Lấy câu trả lời
    answer_ids = request.POST.getlist('answer')
    if not answer_ids:
        messages.warning(request, 'Vui lòng chọn ít nhất một câu trả lời!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Kiểm tra câu trả lời
    is_correct = current_question.check_answer(answer_ids)

    # Lưu câu trả lời
    answers = participant.answers or {}
    answers[str(current_question.id)] = {
        'answer_ids': answer_ids,
        'is_correct': is_correct,
        'timestamp': timezone.now().isoformat()
    }
    participant.answers = answers

    # Cập nhật điểm
    if is_correct:
        participant.score += current_question.points

    participant.save(update_fields=['answers', 'score'])

    if is_correct:
        messages.success(request, 'Chúc mừng! Câu trả lời của bạn đúng!')
    else:
        messages.warning(request, 'Rất tiếc! Câu trả lời của bạn sai!')

    return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

@login_required
@require_POST
def end_live_competition(request, live_competition_id):
    """Kết thúc cuộc thi trực tiếp"""
    live_competition = get_object_or_404(LiveCompetition, id=live_competition_id)

    # Kiểm tra xem người dùng có phải là người tổ chức không
    if live_competition.host != request.user:
        messages.warning(request, 'Chỉ người tổ chức mới có thể kết thúc cuộc thi!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Kiểm tra xem cuộc thi có đang diễn ra không
    if live_competition.status != 'active':
        messages.warning(request, 'Cuộc thi không đang diễn ra!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Kết thúc cuộc thi
    live_competition.status = 'completed'
    live_competition.end_time = timezone.now()
    live_competition.save(update_fields=['status', 'end_time'])

    messages.success(request, 'Cuộc thi đã kết thúc!')
    return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

@login_required
@require_POST
def cancel_live_competition(request, live_competition_id):
    """Hủy cuộc thi trực tiếp"""
    live_competition = get_object_or_404(LiveCompetition, id=live_competition_id)

    # Kiểm tra xem người dùng có phải là người tổ chức không
    if live_competition.host != request.user:
        messages.warning(request, 'Chỉ người tổ chức mới có thể hủy cuộc thi!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Kiểm tra xem cuộc thi có đang chờ bắt đầu hoặc đang diễn ra không
    if live_competition.status not in ['waiting', 'active']:
        messages.warning(request, 'Cuộc thi không thể hủy!')
        return redirect('advanced_learning:live_competition_detail', live_competition_id=live_competition.id)

    # Hủy cuộc thi
    live_competition.status = 'cancelled'
    live_competition.end_time = timezone.now()
    live_competition.save(update_fields=['status', 'end_time'])

    messages.success(request, 'Cuộc thi đã bị hủy!')
    return redirect('advanced_learning:live_competitions')


# View cho thi đấu theo nhóm
@login_required
def competition_teams(request):
    """Hiển thị danh sách các nhóm thi đấu"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    competition_id = request.GET.get('competition', '')

    # Lấy danh sách các nhóm
    teams = CompetitionTeam.objects.all().order_by('-created_at')

    # Áp dụng bộ lọc
    if search_query:
        teams = teams.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(competition__title__icontains=search_query)
        )

    if competition_id:
        teams = teams.filter(competition_id=competition_id)

    # Lấy danh sách các cuộc thi theo nhóm
    team_competitions = CompetitionMode.objects.filter(competition_type='team', is_active=True).order_by('-start_time')

    # Lấy danh sách các nhóm của người dùng
    user_teams = CompetitionTeam.objects.filter(
        Q(leader=request.user) | Q(members__user=request.user)
    ).distinct().values_list('id', flat=True)

    context = {
        'teams': teams,
        'search_query': search_query,
        'selected_competition': competition_id,
        'team_competitions': team_competitions,
        'user_teams': user_teams,
    }

    return render(request, 'advanced_learning/competitions/teams.html', context)

@login_required
def create_team(request, competition_id=None):
    """Tạo nhóm thi đấu mới"""
    if competition_id:
        competition = get_object_or_404(CompetitionMode, id=competition_id, competition_type='team')
    else:
        competition = None

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        competition_id = request.POST.get('competition')

        if not name:
            messages.error(request, 'Vui lòng nhập tên nhóm!')
            return redirect('advanced_learning:create_team')

        if not competition_id:
            messages.error(request, 'Vui lòng chọn cuộc thi!')
            return redirect('advanced_learning:create_team')

        competition = get_object_or_404(CompetitionMode, id=competition_id, competition_type='team')

        # Kiểm tra xem người dùng đã có nhóm trong cuộc thi này chưa
        if CompetitionTeam.objects.filter(competition=competition, leader=request.user).exists():
            messages.warning(request, 'Bạn đã có nhóm trong cuộc thi này rồi!')
            return redirect('advanced_learning:competition_teams')

        if CompetitionParticipant.objects.filter(competition=competition, user=request.user, team__isnull=False).exists():
            messages.warning(request, 'Bạn đã tham gia nhóm khác trong cuộc thi này rồi!')
            return redirect('advanced_learning:competition_teams')

        # Tạo nhóm mới
        team = CompetitionTeam.objects.create(
            name=name,
            description=description,
            competition=competition,
            leader=request.user
        )

        # Tự động tham gia với tư cách là trưởng nhóm
        participant = CompetitionParticipant.objects.filter(user=request.user, competition=competition).first()
        if not participant:
            participant = CompetitionParticipant.objects.create(
                user=request.user,
                competition=competition
            )

        participant.team = team
        participant.save(update_fields=['team'])

        messages.success(request, 'Nhóm đã được tạo thành công!')
        return redirect('advanced_learning:team_detail', team_id=team.id)

    # Lấy danh sách các cuộc thi theo nhóm
    if not competition:
        competitions = CompetitionMode.objects.filter(competition_type='team', is_active=True).order_by('-start_time')
    else:
        competitions = [competition]

    context = {
        'competitions': competitions,
        'selected_competition': competition,
    }

    return render(request, 'advanced_learning/competitions/create_team.html', context)

@login_required
def team_detail(request, team_id):
    """Chi tiết nhóm thi đấu"""
    team = get_object_or_404(CompetitionTeam, id=team_id)

    # Kiểm tra xem người dùng có phải là thành viên của nhóm không
    is_member = CompetitionParticipant.objects.filter(user=request.user, team=team).exists()

    # Kiểm tra xem người dùng có phải là trưởng nhóm không
    is_leader = team.leader == request.user

    # Lấy danh sách thành viên
    members = CompetitionParticipant.objects.filter(team=team).select_related('user')

    # Kiểm tra xem có thể tham gia nhóm không
    can_join = not is_member and team.competition.can_join()

    # Kiểm tra xem người dùng đã tham gia nhóm khác trong cuộc thi này chưa
    has_other_team = False
    if not is_member:
        has_other_team = CompetitionParticipant.objects.filter(
            user=request.user,
            competition=team.competition,
            team__isnull=False
        ).exists()

    context = {
        'team': team,
        'is_member': is_member,
        'is_leader': is_leader,
        'members': members,
        'can_join': can_join,
        'has_other_team': has_other_team,
    }

    return render(request, 'advanced_learning/competitions/team_detail.html', context)

@login_required
@require_POST
def join_team(request, team_id):
    """Tham gia nhóm thi đấu"""
    team = get_object_or_404(CompetitionTeam, id=team_id)

    # Kiểm tra xem người dùng đã tham gia nhóm này chưa
    if CompetitionParticipant.objects.filter(user=request.user, team=team).exists():
        messages.warning(request, 'Bạn đã tham gia nhóm này rồi!')
        return redirect('advanced_learning:team_detail', team_id=team.id)

    # Kiểm tra xem người dùng đã tham gia nhóm khác trong cuộc thi này chưa
    if CompetitionParticipant.objects.filter(user=request.user, competition=team.competition, team__isnull=False).exists():
        messages.warning(request, 'Bạn đã tham gia nhóm khác trong cuộc thi này rồi!')
        return redirect('advanced_learning:team_detail', team_id=team.id)

    # Kiểm tra xem cuộc thi có thể tham gia không
    if not team.competition.can_join():
        messages.warning(request, 'Cuộc thi này không thể tham gia!')
        return redirect('advanced_learning:team_detail', team_id=team.id)

    # Tham gia nhóm
    participant = CompetitionParticipant.objects.filter(user=request.user, competition=team.competition).first()
    if not participant:
        participant = CompetitionParticipant.objects.create(
            user=request.user,
            competition=team.competition
        )

    participant.team = team
    participant.save(update_fields=['team'])

    messages.success(request, 'Bạn đã tham gia nhóm thành công!')
    return redirect('advanced_learning:team_detail', team_id=team.id)

@login_required
@require_POST
def leave_team(request, team_id):
    """Rời khỏi nhóm thi đấu"""
    team = get_object_or_404(CompetitionTeam, id=team_id)

    # Kiểm tra xem người dùng có phải là trưởng nhóm không
    if team.leader == request.user:
        messages.warning(request, 'Trưởng nhóm không thể rời khỏi nhóm! Bạn có thể giải tán nhóm hoặc chuyển quyền trưởng nhóm.')
        return redirect('advanced_learning:team_detail', team_id=team.id)

    # Kiểm tra xem người dùng có phải là thành viên của nhóm không
    participant = CompetitionParticipant.objects.filter(user=request.user, team=team).first()
    if not participant:
        messages.warning(request, 'Bạn không phải là thành viên của nhóm này!')
        return redirect('advanced_learning:team_detail', team_id=team.id)

    # Rời khỏi nhóm
    participant.team = None
    participant.save(update_fields=['team'])

    messages.success(request, 'Bạn đã rời khỏi nhóm thành công!')
    return redirect('advanced_learning:competition_teams')

@login_required
@require_POST
def remove_member(request, team_id, user_id):
    """Xóa thành viên khỏi nhóm"""
    team = get_object_or_404(CompetitionTeam, id=team_id)
    user_to_remove = get_object_or_404(User, id=user_id)

    # Kiểm tra xem người dùng có phải là trưởng nhóm không
    if team.leader != request.user:
        messages.warning(request, 'Chỉ trưởng nhóm mới có thể xóa thành viên!')
        return redirect('advanced_learning:team_detail', team_id=team.id)

    # Không thể xóa trưởng nhóm
    if user_to_remove == team.leader:
        messages.warning(request, 'Không thể xóa trưởng nhóm!')
        return redirect('advanced_learning:team_detail', team_id=team.id)

    # Kiểm tra xem người dùng có phải là thành viên của nhóm không
    participant = CompetitionParticipant.objects.filter(user=user_to_remove, team=team).first()
    if not participant:
        messages.warning(request, 'Người dùng này không phải là thành viên của nhóm!')
        return redirect('advanced_learning:team_detail', team_id=team.id)

    # Xóa thành viên khỏi nhóm
    participant.team = None
    participant.save(update_fields=['team'])

    messages.success(request, f'Đã xóa {user_to_remove.username} khỏi nhóm thành công!')
    return redirect('advanced_learning:team_detail', team_id=team.id)

@login_required
@require_POST
def transfer_leadership(request, team_id, user_id):
    """Chuyển quyền trưởng nhóm"""
    team = get_object_or_404(CompetitionTeam, id=team_id)
    new_leader = get_object_or_404(User, id=user_id)

    # Kiểm tra xem người dùng có phải là trưởng nhóm không
    if team.leader != request.user:
        messages.warning(request, 'Chỉ trưởng nhóm mới có thể chuyển quyền trưởng nhóm!')
        return redirect('advanced_learning:team_detail', team_id=team.id)

    # Kiểm tra xem người dùng mới có phải là thành viên của nhóm không
    if not CompetitionParticipant.objects.filter(user=new_leader, team=team).exists():
        messages.warning(request, 'Người dùng này không phải là thành viên của nhóm!')
        return redirect('advanced_learning:team_detail', team_id=team.id)

    # Chuyển quyền trưởng nhóm
    team.leader = new_leader
    team.save(update_fields=['leader'])

    messages.success(request, f'Đã chuyển quyền trưởng nhóm cho {new_leader.username} thành công!')
    return redirect('advanced_learning:team_detail', team_id=team.id)

@login_required
@require_POST
def disband_team(request, team_id):
    """Giải tán nhóm"""
    team = get_object_or_404(CompetitionTeam, id=team_id)

    # Kiểm tra xem người dùng có phải là trưởng nhóm không
    if team.leader != request.user:
        messages.warning(request, 'Chỉ trưởng nhóm mới có thể giải tán nhóm!')
        return redirect('advanced_learning:team_detail', team_id=team.id)

    # Xóa liên kết của tất cả thành viên với nhóm
    CompetitionParticipant.objects.filter(team=team).update(team=None)

    # Xóa nhóm
    team.delete()

    messages.success(request, 'Nhóm đã được giải tán thành công!')
    return redirect('advanced_learning:competition_teams')


# View cho chia sẻ kết quả thi đấu
@login_required
@require_POST
def share_competition_result(request, competition_id):
    """Chia sẻ kết quả thi đấu lên mạng xã hội"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)

    # Kiểm tra xem người dùng đã tham gia cuộc thi này chưa
    participant = get_object_or_404(CompetitionParticipant, user=request.user, competition=competition)

    # Kiểm tra xem người dùng đã hoàn thành cuộc thi chưa
    if not participant.end_time:
        messages.warning(request, 'Bạn chưa hoàn thành cuộc thi này!')
        return redirect('advanced_learning:competition_result', competition_id=competition.id)

    # Đánh dấu là đã chia sẻ
    participant.is_shared = True
    participant.save(update_fields=['is_shared'])

    # Tạo URL chia sẻ
    share_url = request.build_absolute_uri(reverse('advanced_learning:competition_result', args=[competition.id]))

    # Tạo nội dung chia sẻ
    share_text = f"Tôi đã hoàn thành cuộc thi '{competition.title}' với {participant.score} điểm và xếp hạng #{participant.rank}!"

    # Tạo URL chia sẻ cho các mạng xã hội
    facebook_share_url = f"https://www.facebook.com/sharer/sharer.php?u={share_url}&quote={share_text}"
    twitter_share_url = f"https://twitter.com/intent/tweet?text={share_text}&url={share_url}"
    linkedin_share_url = f"https://www.linkedin.com/shareArticle?mini=true&url={share_url}&title={competition.title}&summary={share_text}"

    context = {
        'competition': competition,
        'participant': participant,
        'share_url': share_url,
        'share_text': share_text,
        'facebook_share_url': facebook_share_url,
        'twitter_share_url': twitter_share_url,
        'linkedin_share_url': linkedin_share_url,
    }

    return render(request, 'advanced_learning/competitions/share_result.html', context)

@login_required
def generate_share_image(request, competition_id):
    """Tạo hình ảnh kết quả để chia sẻ"""
    competition = get_object_or_404(CompetitionMode, id=competition_id)
    participant = get_object_or_404(CompetitionParticipant, user=request.user, competition=competition)

    # Kiểm tra xem người dùng đã hoàn thành cuộc thi chưa
    if not participant.end_time:
        messages.warning(request, 'Bạn chưa hoàn thành cuộc thi này!')
        return redirect('advanced_learning:competition_result', competition_id=competition.id)

    # Tạo hình ảnh chia sẻ
    # TODO: Implement image generation

    # Trả về hình ảnh
    return HttpResponse('Not implemented yet', content_type='text/plain')


# View cho bảng xếp hạng thi đấu
@login_required
def competition_leaderboard(request):
    """Hiển thị bảng xếp hạng tổng hợp của các cuộc thi"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    time_period = request.GET.get('period', 'all')

    # Tính toán thời gian bắt đầu dựa trên khoảng thời gian
    start_date = None
    if time_period == 'day':
        start_date = timezone.now() - timedelta(days=1)
    elif time_period == 'week':
        start_date = timezone.now() - timedelta(weeks=1)
    elif time_period == 'month':
        start_date = timezone.now() - timedelta(days=30)

    # Lấy danh sách người dùng có điểm cao nhất
    participants = CompetitionParticipant.objects.filter(end_time__isnull=False)

    # Áp dụng bộ lọc
    if subject_id:
        participants = participants.filter(competition__subject_id=subject_id)

    if start_date:
        participants = participants.filter(end_time__gte=start_date)

    # Tính tổng điểm và số cuộc thi đã tham gia của mỗi người dùng
    user_stats = participants.values('user').annotate(
        total_score=Sum('score'),
        competitions_count=Count('competition', distinct=True),
        best_rank=Min('rank')
    ).order_by('-total_score')

    # Lấy thông tin người dùng
    for stat in user_stats:
        user = User.objects.get(id=stat['user'])
        stat['username'] = user.username
        stat['full_name'] = f"{user.first_name} {user.last_name}".strip() or user.username

    # Lấy danh sách các chủ đề
    subjects = Subject.objects.all()

    # Lấy thứ hạng của người dùng hiện tại
    current_user_rank = None
    for i, stat in enumerate(user_stats):
        if stat['user'] == request.user.id:
            current_user_rank = i + 1
            break

    context = {
        'user_stats': user_stats,
        'subjects': subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
        'selected_period': time_period,
        'current_user_rank': current_user_rank,
    }

    return render(request, 'advanced_learning/competitions/leaderboard.html', context)

@login_required
def competition_achievements(request):
    """Hiển thị danh sách các thành tích liên quan đến cuộc thi"""
    # Lấy danh sách các thành tích của người dùng
    user_achievements = UserAchievement.objects.filter(
        user=request.user,
        achievement__achievement_type='competition'
    ).select_related('achievement').order_by('-earned_at')

    # Lấy danh sách các thành tích có thể đạt được
    all_achievements = Achievement.objects.filter(achievement_type='competition')

    # Lấy danh sách ID của các thành tích đã đạt được
    earned_achievement_ids = user_achievements.values_list('achievement_id', flat=True)

    # Lọc các thành tích chưa đạt được
    unearned_achievements = all_achievements.exclude(id__in=earned_achievement_ids)

    # Lọc các thành tích ẩn chưa đạt được
    unearned_visible_achievements = unearned_achievements.filter(is_hidden=False)

    context = {
        'user_achievements': user_achievements,
        'unearned_achievements': unearned_visible_achievements,
    }

    return render(request, 'advanced_learning/competitions/achievements.html', context)
