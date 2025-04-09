from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from datetime import timedelta
import json
from .models import FlashcardSet, Flashcard, SpacedRepetitionSchedule
from .forms import FlashcardSetForm, FlashcardForm, AutoGenerateFlashcardsForm, TextToFlashcardsForm
from .services import generate_flashcards_from_lesson
from .auto_flashcard_service import AutoFlashcardService
from content.models import Subject, Topic, Lesson

def flashcard_list(request):
    """Hiển thị danh sách các bộ flashcard"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    format_type = request.GET.get('format', '')

    # Lấy danh sách bộ flashcard
    flashcard_sets = FlashcardSet.objects.all().select_related('lesson__topic__subject')

    # Áp dụng bộ lọc
    if search_query:
        flashcard_sets = flashcard_sets.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(lesson__title__icontains=search_query) |
            Q(lesson__topic__name__icontains=search_query) |
            Q(lesson__topic__subject__name__icontains=search_query)
        )

    if subject_id:
        flashcard_sets = flashcard_sets.filter(lesson__topic__subject_id=subject_id)

    # Lấy danh sách các chủ đề cho bộ lọc
    subjects = Subject.objects.all()

    # Đếm số flashcard cần ôn tập hôm nay nếu đã đăng nhập
    due_count = 0
    if request.user.is_authenticated:
        today = timezone.now()
        due_count = SpacedRepetitionSchedule.objects.filter(
            user=request.user,
            next_review_date__lte=today
        ).count()

    context = {
        'flashcard_sets': flashcard_sets,
        'subjects': subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
        'due_count': due_count
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'flashcards/flashcard_list_partial.html', context)

    return render(request, 'flashcards/flashcard_list.html', context)

def flashcard_set_detail(request, flashcard_set_id):
    """Hiển thị chi tiết bộ flashcard và các flashcard trong bộ"""
    flashcard_set = get_object_or_404(FlashcardSet, id=flashcard_set_id)
    flashcards = flashcard_set.flashcards.all()
    format_type = request.GET.get('format', '')

    # Tính toán tiến độ ôn tập nếu người dùng đã đăng nhập
    mastered_count = 0
    mastered_percentage = 0
    due_count = 0

    if request.user.is_authenticated and flashcards.exists():
        # Đếm số flashcard đã thuộc (recall_level = 3)
        mastered_count = SpacedRepetitionSchedule.objects.filter(
            user=request.user,
            flashcard__in=flashcards,
            recall_level=3
        ).count()

        # Tính phần trăm đã thuộc
        mastered_percentage = int((mastered_count / flashcards.count()) * 100)

        # Đếm số flashcard cần ôn tập hôm nay
        today = timezone.now()
        due_count = SpacedRepetitionSchedule.objects.filter(
            user=request.user,
            flashcard__in=flashcards,
            next_review_date__lte=today
        ).count()

    context = {
        'flashcard_set': flashcard_set,
        'flashcards': flashcards,
        'mastered_count': mastered_count,
        'mastered_percentage': mastered_percentage,
        'due_count': due_count
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'flashcards/flashcard_set_detail_partial.html', context)

    return render(request, 'flashcards/flashcard_set_detail.html', context)

@login_required
def update_recall_level(request):
    """Cập nhật mức độ nhớ của flashcard và lên lịch ôn tập tiếp theo"""
    if request.method == 'POST':
        try:
            # Xử lý cả request AJAX và HTMX
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            flashcard_id = data.get('flashcard_id')
            recall_level = int(data.get('recall_level'))

            if not flashcard_id or recall_level not in [1, 2, 3]:
                if request.htmx:
                    return render(request, 'flashcards/error_message.html', {
                        'error': 'Dữ liệu không hợp lệ'
                    })
                return JsonResponse({'success': False, 'error': 'Dữ liệu không hợp lệ'})

            flashcard = get_object_or_404(Flashcard, id=flashcard_id)

            # Tìm lịch ôn tập hiện tại nếu có
            existing_schedule = SpacedRepetitionSchedule.objects.filter(
                user=request.user,
                flashcard=flashcard
            ).first()

            # Tính ngày ôn tập tiếp theo dựa trên mức độ nhớ
            now = timezone.now()
            if recall_level == 1:  # Khó nhớ
                next_review_date = now + timedelta(days=1)
            elif recall_level == 2:  # Nhớ mờ mờ
                next_review_date = now + timedelta(days=3)
            else:  # Nhớ rõ
                # Tăng khoảng cách ôn tập dựa trên số lần đã ôn tập
                if existing_schedule:
                    days = min(30, 7 * (existing_schedule.review_count + 1))
                else:
                    days = 7
                next_review_date = now + timedelta(days=days)

            # Cập nhật hoặc tạo lịch ôn tập
            schedule, created = SpacedRepetitionSchedule.objects.get_or_create(
                user=request.user,
                flashcard=flashcard,
                defaults={
                    'next_review_date': next_review_date,
                    'recall_level': recall_level,
                    'review_count': 1
                }
            )

            # Nếu đã tồn tại, cập nhật thông tin
            if not created:
                schedule.next_review_date = next_review_date
                schedule.recall_level = recall_level
                schedule.review_count += 1
                schedule.save()

            # Trả về kết quả phù hợp với loại request
            if request.htmx:
                # Tính toán số flashcard còn lại cần ôn tập
                remaining_count = SpacedRepetitionSchedule.objects.filter(
                    user=request.user,
                    next_review_date__lte=timezone.now()
                ).count()

                return render(request, 'flashcards/recall_feedback.html', {
                    'recall_level': recall_level,
                    'next_review_date': next_review_date,
                    'remaining_count': remaining_count
                })

            return JsonResponse({
                'success': True,
                'next_review_date': next_review_date.strftime('%d/%m/%Y'),
                'recall_level': recall_level
            })

        except Exception as e:
            if request.htmx:
                return render(request, 'flashcards/error_message.html', {
                    'error': str(e)
                })
            return JsonResponse({'success': False, 'error': str(e)})

    if request.htmx:
        return render(request, 'flashcards/error_message.html', {
            'error': 'Phương thức không được hỗ trợ'
        })
    return JsonResponse({'success': False, 'error': 'Phương thức không được hỗ trợ'})

@login_required
def due_flashcards(request):
    """Hiển thị các flashcard cần ôn tập hôm nay"""
    today = timezone.now()
    format_type = request.GET.get('format', '')

    due_schedules = SpacedRepetitionSchedule.objects.filter(
        user=request.user,
        next_review_date__lte=today
    ).select_related('flashcard__flashcard_set__lesson__topic__subject')

    # Nhóm các flashcard theo bộ
    flashcard_sets = {}
    for schedule in due_schedules:
        flashcard_set = schedule.flashcard.flashcard_set
        if flashcard_set.id not in flashcard_sets:
            flashcard_sets[flashcard_set.id] = {
                'set': flashcard_set,
                'flashcards': [],
                'count': 0
            }

        flashcard_sets[flashcard_set.id]['flashcards'].append(schedule.flashcard)
        flashcard_sets[flashcard_set.id]['count'] += 1

    context = {
        'flashcard_sets': flashcard_sets.values(),
        'total_due': due_schedules.count()
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'flashcards/due_flashcards_partial.html', context)

    return render(request, 'flashcards/due_flashcards.html', context)

@login_required
def get_topics(request):
    """Lấy danh sách các chủ đề con theo chủ đề chính"""
    subject_id = request.GET.get('subject', '')
    topics = []

    if subject_id:
        topics = Topic.objects.filter(subject_id=subject_id).order_by('order')

    return render(request, 'flashcards/topic_options.html', {'topics': topics})

@login_required
def get_lessons(request):
    """Lấy danh sách các bài học theo chủ đề con"""
    topic_id = request.GET.get('topic', '')
    lessons = []

    if topic_id:
        lessons = Lesson.objects.filter(topic_id=topic_id).order_by('order')

    return render(request, 'flashcards/lesson_options.html', {'lessons': lessons})

@login_required
def auto_generate_flashcards(request):
    """Tự động tạo flashcards từ bài học"""
    if request.method == 'POST':
        form = AutoGenerateFlashcardsForm(request.POST)
        if form.is_valid():
            # Lấy dữ liệu từ form
            lesson = form.cleaned_data['lesson']
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            max_cards = form.cleaned_data['max_cards']

            # Tạo bộ flashcard mới
            flashcard_set = FlashcardSet.objects.create(
                user=request.user,
                lesson=lesson,
                title=title,
                description=description,
                is_auto_generated=True
            )

            # Tạo các flashcard từ nội dung bài học
            flashcard_pairs = generate_flashcards_from_lesson(lesson, max_cards=max_cards)

            # Thêm các flashcard vào bộ
            for i, (front, back) in enumerate(flashcard_pairs):
                Flashcard.objects.create(
                    flashcard_set=flashcard_set,
                    front=front,
                    back=back,
                    order=i+1,
                    is_auto_generated=True
                )

            messages.success(request, f'Đã tạo {len(flashcard_pairs)} flashcard từ bài học "{lesson.title}"!')
            return redirect('flashcard_set_detail', flashcard_set_id=flashcard_set.id)
    else:
        form = AutoGenerateFlashcardsForm()

    context = {
        'form': form,
        'title': 'Tự động tạo Flashcards'
    }

    return render(request, 'flashcards/auto_generate_flashcards.html', context)


@login_required
def text_to_flashcards(request):
    """Tạo flashcards từ văn bản"""
    if request.method == 'POST':
        form = TextToFlashcardsForm(request.POST, user=request.user)
        if form.is_valid():
            text = form.cleaned_data['text']
            flashcard_set = form.cleaned_data['flashcard_set']
            language = form.cleaned_data['language']
            max_cards = form.cleaned_data['max_cards']
            use_ai = form.cleaned_data['use_ai']

            # Tạo flashcards từ văn bản
            service = AutoFlashcardService()

            if use_ai:
                flashcards = service.generate_flashcards_with_ai(text, language, max_cards)
            else:
                flashcards = service.generate_flashcards(text, language, max_cards)

            # Lưu các flashcard vào database
            for i, card_data in enumerate(flashcards):
                Flashcard.objects.create(
                    flashcard_set=flashcard_set,
                    front=card_data['front'],
                    back=card_data['back'],
                    order=i
                )

            messages.success(request, f'Đã tạo {len(flashcards)} flashcard từ văn bản.')
            return redirect('flashcard_set_detail', pk=flashcard_set.id)
    else:
        form = TextToFlashcardsForm(user=request.user)

    context = {
        'form': form,
        'title': 'Tạo Flashcards từ văn bản'
    }

    return render(request, 'flashcards/text_to_flashcards.html', context)


@login_required
def preview_text_flashcards(request):
    """Xem trước các flashcard được tạo từ văn bản"""
    if request.method == 'POST':
        data = json.loads(request.body)
        text = data.get('text', '')
        language = data.get('language', 'vi')
        max_cards = int(data.get('max_cards', 10))
        use_ai = data.get('use_ai', True)

        # Tạo flashcards từ văn bản
        service = AutoFlashcardService()

        if use_ai:
            flashcards = service.generate_flashcards_with_ai(text, language, max_cards)
        else:
            flashcards = service.generate_flashcards(text, language, max_cards)

        return JsonResponse({
            'success': True,
            'flashcards': flashcards
        })

    return JsonResponse({'success': False, 'error': 'Phương thức không hợp lệ'})


@login_required
def get_subjects(request):
    """Lấy danh sách các chủ đề"""
    subjects = Subject.objects.all().values('id', 'name')
    return JsonResponse({'subjects': list(subjects)})
