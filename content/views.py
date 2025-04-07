from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Subject, Topic, Lesson
from accounts.models import UserProgress
from flashcards.models import FlashcardSet
from quizzes.models import Quiz

def home(request):
    """Trang chủ của ứng dụng"""
    # Lấy các chủ đề nổi bật
    featured_subjects = Subject.objects.all()[:4]  # Lấy 4 chủ đề đầu tiên để hiển thị

    # Thống kê cho người dùng đã đăng nhập
    completed_lessons_count = 0
    flashcards_due_count = 0
    quiz_attempts_count = 0
    study_time_hours = 0
    user_favorites = []

    if request.user.is_authenticated:
        # Đếm số bài học đã hoàn thành
        completed_lessons_count = UserProgress.objects.filter(user=request.user, completed=True).count()

        # Lấy các chủ đề yêu thích của người dùng
        user_favorites = request.user.profile.favorite_subjects.all()

        # Các thống kê khác sẽ được thêm sau

    context = {
        'featured_subjects': featured_subjects,
        'completed_lessons_count': completed_lessons_count,
        'flashcards_due_count': flashcards_due_count,
        'quiz_attempts_count': quiz_attempts_count,
        'study_time_hours': study_time_hours,
        'user_favorites': user_favorites
    }

    return render(request, 'content/home.html', context)

def about(request):
    """Trang giới thiệu"""
    return render(request, 'content/about.html')

def subject_list(request):
    """Hiển thị danh sách các chủ đề"""
    subjects = Subject.objects.all()
    return render(request, 'content/subject_list.html', {'subjects': subjects})

def subject_detail(request, slug):
    """Hiển thị chi tiết chủ đề và các chủ đề con"""
    subject = get_object_or_404(Subject, slug=slug)
    topics = subject.topics.all()

    # Tính toán tiến độ học tập nếu người dùng đã đăng nhập
    progress_percentage = 0
    completed_lessons = 0
    total_lessons = 0

    if request.user.is_authenticated:
        # Đếm tổng số bài học trong chủ đề
        for topic in topics:
            total_lessons += topic.lessons.count()

        # Đếm số bài học đã hoàn thành
        if total_lessons > 0:
            # Lấy tất cả các bài học trong chủ đề
            lesson_ids = []
            for topic in topics:
                lesson_ids.extend(topic.lessons.values_list('id', flat=True))

            # Đếm số bài học đã hoàn thành
            completed_lessons = UserProgress.objects.filter(
                user=request.user,
                lesson_id__in=lesson_ids,
                completed=True
            ).count()

            # Tính phần trăm hoàn thành
            progress_percentage = int((completed_lessons / total_lessons) * 100)

    # Kiểm tra xem chủ đề có được yêu thích không
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = subject in request.user.profile.favorite_subjects.all()

    # Lấy danh sách ID của các bài học đã hoàn thành
    completed_lessons_ids = []
    if request.user.is_authenticated:
        completed_lessons_ids = UserProgress.objects.filter(
            user=request.user,
            lesson__topic__subject=subject,
            completed=True
        ).values_list('lesson_id', flat=True)

    context = {
        'subject': subject,
        'topics': topics,
        'progress_percentage': progress_percentage,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'is_favorite': is_favorite,
        'completed_lessons_ids': completed_lessons_ids
    }

    return render(request, 'content/subject_detail.html', context)

def lesson_detail(request, subject_slug, topic_slug, lesson_slug):
    """Hiển thị chi tiết bài học"""
    subject = get_object_or_404(Subject, slug=subject_slug)
    topic = get_object_or_404(Topic, slug=topic_slug, subject=subject)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, topic=topic)

    # Lấy bài học trước và sau
    lessons = list(topic.lessons.order_by('order'))
    lesson_index = lessons.index(lesson)
    prev_lesson = lessons[lesson_index - 1] if lesson_index > 0 else None
    next_lesson = lessons[lesson_index + 1] if lesson_index < len(lessons) - 1 else None

    # Lấy các bộ flashcard và quiz liên quan
    flashcard_sets = FlashcardSet.objects.filter(lesson=lesson)
    quizzes = Quiz.objects.filter(lesson=lesson)

    # Cập nhật tiến độ người dùng
    user_progress = None
    if request.user.is_authenticated:
        user_progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'last_accessed': timezone.now()}
        )
        if not created:
            user_progress.last_accessed = timezone.now()
            user_progress.save()

    context = {
        'subject': subject,
        'topic': topic,
        'lesson': lesson,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'flashcard_sets': flashcard_sets,
        'quizzes': quizzes,
        'user_progress': user_progress
    }

    return render(request, 'content/lesson_detail.html', context)

@login_required
def mark_lesson_complete(request, lesson_id):
    """Đánh dấu bài học đã hoàn thành"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    user_progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'completed': True, 'completion_date': timezone.now()}
    )

    if not created and not user_progress.completed:
        user_progress.completed = True
        user_progress.completion_date = timezone.now()
        user_progress.save()
        messages.success(request, f'Đã đánh dấu bài học "{lesson.title}" là hoàn thành!')
    elif not created:
        user_progress.completed = False
        user_progress.completion_date = None
        user_progress.save()
        messages.info(request, f'Đã đánh dấu bài học "{lesson.title}" là chưa hoàn thành!')
    else:
        messages.success(request, f'Đã đánh dấu bài học "{lesson.title}" là hoàn thành!')

    return redirect('lesson_detail',
                    subject_slug=lesson.topic.subject.slug,
                    topic_slug=lesson.topic.slug,
                    lesson_slug=lesson.slug)

@login_required
def toggle_favorite_subject(request, subject_id):
    """Thêm/xóa chủ đề yêu thích"""
    subject = get_object_or_404(Subject, id=subject_id)
    user_profile = request.user.profile

    if subject in user_profile.preferred_subjects.all():
        user_profile.preferred_subjects.remove(subject)
        messages.info(request, f'Đã xóa "{subject.name}" khỏi danh sách yêu thích')
    else:
        user_profile.preferred_subjects.add(subject)
        messages.success(request, f'Đã thêm "{subject.name}" vào danh sách yêu thích')

    return redirect('subject_detail', slug=subject.slug)
