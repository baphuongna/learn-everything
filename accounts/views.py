from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.urls import reverse_lazy
from .models import UserProfile, UserProgress, StudySession
from content.models import Subject, Lesson
from flashcards.models import SpacedRepetitionSchedule
from quizzes.models import QuizAttempt
from .forms import UserProfileForm, UserForm, StudySessionForm, CustomUserCreationForm, CustomAuthenticationForm

def register(request):
    """Trang đăng ký người dùng mới"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Tài khoản đã được tạo thành công! Bây giờ bạn có thể đăng nhập.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    """View đăng nhập tùy chỉnh sử dụng form với crispy-forms"""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

@login_required
def profile(request):
    """Trang hồ sơ người dùng"""
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Hồ sơ của bạn đã được cập nhật!')
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def progress(request):
    """Trang theo dõi tiến độ học tập"""
    # Lấy tiến độ học tập của người dùng
    user_progress = UserProgress.objects.filter(user=request.user).select_related('lesson__topic__subject')

    # Tổng hợp tiến độ theo chủ đề
    subjects_progress = {}
    for progress in user_progress:
        subject = progress.lesson.topic.subject
        if subject.id not in subjects_progress:
            subjects_progress[subject.id] = {
                'subject': subject,
                'completed': 0,
                'total': 0,
                'percentage': 0
            }

        subjects_progress[subject.id]['total'] += 1
        if progress.completed:
            subjects_progress[subject.id]['completed'] += 1

    # Tính phần trăm hoàn thành cho mỗi chủ đề
    for subject_id in subjects_progress:
        total = subjects_progress[subject_id]['total']
        if total > 0:
            completed = subjects_progress[subject_id]['completed']
            subjects_progress[subject_id]['percentage'] = int((completed / total) * 100)

    # Lấy các phiên học gần đây
    recent_sessions = StudySession.objects.filter(user=request.user).order_by('-start_time')[:5]

    # Tính tổng thời gian học trong 7 ngày gần đây
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)
    weekly_study_time = StudySession.objects.filter(
        user=request.user,
        start_time__gte=seven_days_ago
    ).aggregate(total_minutes=Sum('duration_minutes'))['total_minutes'] or 0

    # Lấy các flashcard cần ôn tập hôm nay
    today = timezone.now()
    flashcards_due = SpacedRepetitionSchedule.objects.filter(
        user=request.user,
        next_review_date__lte=today
    ).select_related('flashcard__flashcard_set__lesson')

    context = {
        'subjects_progress': subjects_progress.values(),
        'recent_sessions': recent_sessions,
        'weekly_study_time': weekly_study_time,
        'flashcards_due': flashcards_due,
        'study_session_form': StudySessionForm()
    }

    return render(request, 'accounts/progress.html', context)

@login_required
def record_study_session(request):
    """Ghi lại phiên học tập"""
    if request.method == 'POST':
        form = StudySessionForm(request.POST)
        if form.is_valid():
            study_session = form.save(commit=False)
            study_session.user = request.user
            study_session.save()
            messages.success(request, 'Phiên học tập đã được ghi lại thành công!')
            return redirect('progress')
    else:
        form = StudySessionForm()

    return render(request, 'accounts/record_study_session.html', {'form': form})
