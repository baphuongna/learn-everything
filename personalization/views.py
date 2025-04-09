from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg, Count
from django.utils import timezone

from .models import (
    LearningPathway, PathwayStep, LearningPreference, ContentRecommendation,
    UserInteraction, UserStrengthWeakness, UIPreference, StudyReminder
)
from .forms import (
    LearningPathwayForm, PathwayStepForm, LearningPreferenceForm, UIPreferenceForm,
    StudyReminderForm, UserStrengthWeaknessForm
)
from content.models import Subject, Topic, Lesson

# Views cho Lộ trình học tập cá nhân hóa
@login_required
def learning_pathway_list(request):
    """Hiển thị danh sách lộ trình học tập của người dùng"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    difficulty = request.GET.get('difficulty', '')
    status = request.GET.get('status', '')
    format_type = request.GET.get('format', '')

    # Lấy danh sách lộ trình
    pathways = LearningPathway.objects.filter(user=request.user).order_by('-created_at')

    # Áp dụng bộ lọc
    if search_query:
        pathways = pathways.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if subject_id:
        pathways = pathways.filter(subject_id=subject_id)

    if difficulty:
        pathways = pathways.filter(difficulty_level=difficulty)

    if status:
        if status == 'active':
            pathways = pathways.filter(is_active=True)
        elif status == 'inactive':
            pathways = pathways.filter(is_active=False)

    # Lấy danh sách các chủ đề cho bộ lọc
    subjects = Subject.objects.all()

    # Lấy các lộ trình đang hoạt động cho HTMX partial
    active_pathways = pathways.filter(is_active=True)[:5] if format_type == 'partial' else None

    context = {
        'pathways': pathways,
        'active_pathways': active_pathways,
        'subjects': subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
        'selected_difficulty': difficulty,
        'selected_status': status,
        'difficulty_levels': LearningPathway.DIFFICULTY_LEVELS,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'personalization/learning_pathway/list_partial.html', context)

    return render(request, 'personalization/learning_pathway/list.html', context)

@login_required
def learning_pathway_detail(request, pathway_id):
    """Hiển thị chi tiết lộ trình học tập"""
    pathway = get_object_or_404(LearningPathway, id=pathway_id, user=request.user)
    steps = pathway.pathway_steps.all().order_by('order')

    # Tính toán tiến độ
    progress = pathway.get_progress_percentage()

    context = {
        'pathway': pathway,
        'steps': steps,
        'progress': progress,
    }

    # Kiểm tra nếu là request HTMX
    if request.GET.get('format') == 'partial' or request.htmx:
        return render(request, 'personalization/learning_pathway/detail_partial.html', context)

    return render(request, 'personalization/learning_pathway/detail.html', context)

@login_required
def learning_pathway_create(request):
    """Tạo lộ trình học tập mới"""
    if request.method == 'POST':
        form = LearningPathwayForm(request.POST)
        if form.is_valid():
            pathway = form.save(commit=False)
            pathway.user = request.user
            pathway.save()

            messages.success(request, 'Lộ trình học tập đã được tạo thành công!')
            return redirect('learning_pathway_detail', pathway_id=pathway.id)
    else:
        form = LearningPathwayForm()

    context = {
        'form': form,
        'title': 'Tạo lộ trình học tập mới',
    }

    return render(request, 'personalization/learning_pathway/form.html', context)

@login_required
def learning_pathway_update(request, pathway_id):
    """Cập nhật lộ trình học tập"""
    pathway = get_object_or_404(LearningPathway, id=pathway_id, user=request.user)

    if request.method == 'POST':
        form = LearningPathwayForm(request.POST, instance=pathway)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lộ trình học tập đã được cập nhật thành công!')
            return redirect('learning_pathway_detail', pathway_id=pathway.id)
    else:
        form = LearningPathwayForm(instance=pathway)

    context = {
        'form': form,
        'pathway': pathway,
        'title': 'Cập nhật lộ trình học tập',
    }

    return render(request, 'personalization/learning_pathway/form.html', context)

@login_required
def learning_pathway_delete(request, pathway_id):
    """Xóa lộ trình học tập"""
    pathway = get_object_or_404(LearningPathway, id=pathway_id, user=request.user)

    if request.method == 'POST':
        pathway.delete()
        messages.success(request, 'Lộ trình học tập đã được xóa thành công!')
        return redirect('learning_pathway_list')

    context = {
        'pathway': pathway,
    }

    return render(request, 'personalization/learning_pathway/delete.html', context)

@login_required
def pathway_step_create(request, pathway_id):
    """Tạo bước mới trong lộ trình học tập"""
    pathway = get_object_or_404(LearningPathway, id=pathway_id, user=request.user)

    if request.method == 'POST':
        form = PathwayStepForm(request.POST)
        if form.is_valid():
            step = form.save(commit=False)
            step.pathway = pathway
            step.save()

            messages.success(request, 'Bước học tập đã được tạo thành công!')
            return redirect('learning_pathway_detail', pathway_id=pathway.id)
    else:
        # Tự động điền thứ tự tiếp theo
        next_order = pathway.pathway_steps.count() + 1
        form = PathwayStepForm(initial={'order': next_order})

    context = {
        'form': form,
        'pathway': pathway,
        'title': 'Thêm bước học tập mới',
    }

    return render(request, 'personalization/pathway_step/form.html', context)

@login_required
def pathway_step_update(request, step_id):
    """Cập nhật bước trong lộ trình học tập"""
    step = get_object_or_404(PathwayStep, id=step_id, pathway__user=request.user)
    pathway = step.pathway

    if request.method == 'POST':
        form = PathwayStepForm(request.POST, instance=step)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bước học tập đã được cập nhật thành công!')
            return redirect('learning_pathway_detail', pathway_id=pathway.id)
    else:
        form = PathwayStepForm(instance=step)

    context = {
        'form': form,
        'step': step,
        'pathway': pathway,
        'title': 'Cập nhật bước học tập',
    }

    return render(request, 'personalization/pathway_step/form.html', context)

@login_required
def pathway_step_delete(request, step_id):
    """Xóa bước trong lộ trình học tập"""
    step = get_object_or_404(PathwayStep, id=step_id, pathway__user=request.user)
    pathway = step.pathway

    if request.method == 'POST':
        step.delete()
        # Cập nhật lại thứ tự các bước còn lại
        for i, s in enumerate(pathway.pathway_steps.all().order_by('order')):
            s.order = i + 1
            s.save()

        messages.success(request, 'Bước học tập đã được xóa thành công!')
        return redirect('learning_pathway_detail', pathway_id=pathway.id)

    context = {
        'step': step,
        'pathway': pathway,
    }

    return render(request, 'personalization/pathway_step/delete.html', context)

@login_required
def pathway_step_complete(request, step_id):
    """Hoàn thành bước trong lộ trình học tập"""
    step = get_object_or_404(PathwayStep, id=step_id, pathway__user=request.user)
    pathway = step.pathway

    if not step.is_completed:
        step.mark_as_completed()
        messages.success(request, f'Chúc mừng! Bạn đã hoàn thành bước "{step.title}"')

    # Nếu là request HTMX, trả về partial view
    if request.htmx:
        steps = pathway.pathway_steps.all().order_by('order')
        progress = pathway.get_progress_percentage()

        context = {
            'pathway': pathway,
            'steps': steps,
            'progress': progress,
        }

        # Thêm header HX-Trigger để hiển thị thông báo
        response = render(request, 'personalization/learning_pathway/detail_partial.html', context)
        response['HX-Trigger'] = '{"showMessage": {"message": "Bước "%s" đã được hoàn thành!", "type": "success"}}' % step.title
        return response

    return redirect('learning_pathway_detail', pathway_id=pathway.id)

# Views cho Sở thích học tập
@login_required
def learning_preference(request):
    """Quản lý sở thích học tập của người dùng"""
    # Lấy hoặc tạo sở thích học tập
    preference, created = LearningPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = LearningPreferenceForm(request.POST, instance=preference, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sở thích học tập đã được cập nhật thành công!')
            return redirect('dashboard')
    else:
        form = LearningPreferenceForm(instance=preference, user=request.user)

    context = {
        'form': form,
        'preference': preference,
    }

    return render(request, 'personalization/learning_preference/form.html', context)

# Views cho Tùy chỉnh giao diện
@login_required
def ui_preference(request):
    """Quản lý tùy chỉnh giao diện của người dùng"""
    # Lấy hoặc tạo tùy chỉnh giao diện
    preference, created = UIPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UIPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tùy chỉnh giao diện đã được cập nhật thành công!')
            return redirect('dashboard')
    else:
        form = UIPreferenceForm(instance=preference)

    context = {
        'form': form,
        'preference': preference,
    }

    return render(request, 'personalization/ui_preference/form.html', context)

# Views cho Nhắc nhở học tập
@login_required
def study_reminder_list(request):
    """Hiển thị danh sách nhắc nhở học tập của người dùng"""
    reminders = StudyReminder.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'reminders': reminders,
    }

    return render(request, 'personalization/study_reminder/list.html', context)

@login_required
def study_reminder_create(request):
    """Tạo nhắc nhở học tập mới"""
    if request.method == 'POST':
        form = StudyReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()

            messages.success(request, 'Nhắc nhở học tập đã được tạo thành công!')
            return redirect('study_reminder_list')
    else:
        form = StudyReminderForm()

    context = {
        'form': form,
        'title': 'Tạo nhắc nhở học tập mới',
    }

    return render(request, 'personalization/study_reminder/form.html', context)

@login_required
def study_reminder_update(request, reminder_id):
    """Cập nhật nhắc nhở học tập"""
    reminder = get_object_or_404(StudyReminder, id=reminder_id, user=request.user)

    if request.method == 'POST':
        form = StudyReminderForm(request.POST, instance=reminder)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nhắc nhở học tập đã được cập nhật thành công!')
            return redirect('study_reminder_list')
    else:
        form = StudyReminderForm(instance=reminder)

    context = {
        'form': form,
        'reminder': reminder,
        'title': 'Cập nhật nhắc nhở học tập',
    }

    return render(request, 'personalization/study_reminder/form.html', context)

@login_required
def study_reminder_delete(request, reminder_id):
    """Xóa nhắc nhở học tập"""
    reminder = get_object_or_404(StudyReminder, id=reminder_id, user=request.user)

    if request.method == 'POST':
        reminder.delete()
        messages.success(request, 'Nhắc nhở học tập đã được xóa thành công!')
        return redirect('study_reminder_list')

    context = {
        'reminder': reminder,
    }

    return render(request, 'personalization/study_reminder/delete.html', context)

@login_required
def study_reminder_toggle(request, reminder_id):
    """Bật/tắt nhắc nhở học tập"""
    reminder = get_object_or_404(StudyReminder, id=reminder_id, user=request.user)
    reminder.is_active = not reminder.is_active
    reminder.save()

    status = 'đã được bật' if reminder.is_active else 'đã được tắt'
    messages.success(request, f'Nhắc nhở học tập {status} thành công!')

    return redirect('study_reminder_list')

# Views cho Phân tích điểm mạnh/yếu
@login_required
def strength_weakness_list(request):
    """Hiển thị danh sách điểm mạnh/yếu của người dùng"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    strength_type = request.GET.get('type', '')

    # Lấy danh sách điểm mạnh/yếu
    assessments = UserStrengthWeakness.objects.filter(user=request.user).order_by('-proficiency_score')

    # Áp dụng bộ lọc
    if search_query:
        assessments = assessments.filter(
            Q(subject__name__icontains=search_query) |
            Q(topic__name__icontains=search_query) |
            Q(notes__icontains=search_query)
        )

    if subject_id:
        assessments = assessments.filter(subject_id=subject_id)

    if strength_type:
        if strength_type == 'strength':
            assessments = assessments.filter(is_strength=True)
        elif strength_type == 'weakness':
            assessments = assessments.filter(is_strength=False)

    # Lấy danh sách các chủ đề cho bộ lọc
    subjects = Subject.objects.all()

    # Tính toán thống kê
    strengths_count = assessments.filter(is_strength=True).count()
    weaknesses_count = assessments.filter(is_strength=False).count()
    avg_proficiency = assessments.aggregate(Avg('proficiency_score'))['proficiency_score__avg'] or 0

    context = {
        'assessments': assessments,
        'subjects': subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
        'selected_type': strength_type,
        'strengths_count': strengths_count,
        'weaknesses_count': weaknesses_count,
        'avg_proficiency': avg_proficiency,
    }

    return render(request, 'personalization/strength_weakness/list.html', context)

@login_required
def strength_weakness_create(request):
    """Tạo đánh giá điểm mạnh/yếu mới"""
    if request.method == 'POST':
        form = UserStrengthWeaknessForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.user = request.user
            assessment.save()

            strength_or_weakness = 'điểm mạnh' if assessment.is_strength else 'điểm yếu'
            messages.success(request, f'Đánh giá {strength_or_weakness} đã được tạo thành công!')
            return redirect('strength_weakness_list')
    else:
        form = UserStrengthWeaknessForm()

    context = {
        'form': form,
        'title': 'Tạo đánh giá điểm mạnh/yếu mới',
    }

    return render(request, 'personalization/strength_weakness/form.html', context)

@login_required
def strength_weakness_update(request, assessment_id):
    """Cập nhật đánh giá điểm mạnh/yếu"""
    assessment = get_object_or_404(UserStrengthWeakness, id=assessment_id, user=request.user)

    if request.method == 'POST':
        form = UserStrengthWeaknessForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            strength_or_weakness = 'điểm mạnh' if assessment.is_strength else 'điểm yếu'
            messages.success(request, f'Đánh giá {strength_or_weakness} đã được cập nhật thành công!')
            return redirect('strength_weakness_list')
    else:
        form = UserStrengthWeaknessForm(instance=assessment)

    context = {
        'form': form,
        'assessment': assessment,
        'title': 'Cập nhật đánh giá điểm mạnh/yếu',
    }

    return render(request, 'personalization/strength_weakness/form.html', context)

@login_required
def strength_weakness_delete(request, assessment_id):
    """Xóa đánh giá điểm mạnh/yếu"""
    assessment = get_object_or_404(UserStrengthWeakness, id=assessment_id, user=request.user)

    if request.method == 'POST':
        assessment.delete()
        messages.success(request, 'Đánh giá đã được xóa thành công!')
        return redirect('strength_weakness_list')

    context = {
        'assessment': assessment,
    }

    return render(request, 'personalization/strength_weakness/delete.html', context)

# Views cho Đề xuất nội dung
@login_required
def content_recommendation_list(request):
    """Hiển thị danh sách đề xuất nội dung cho người dùng"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    rec_type = request.GET.get('type', '')
    viewed = request.GET.get('viewed', '')

    # Lấy danh sách đề xuất
    recommendations = ContentRecommendation.objects.filter(user=request.user).order_by('-relevance_score', '-created_at')

    # Áp dụng bộ lọc
    if search_query:
        recommendations = recommendations.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if subject_id:
        recommendations = recommendations.filter(subject_id=subject_id)

    if rec_type:
        recommendations = recommendations.filter(recommendation_type=rec_type)

    if viewed:
        if viewed == 'viewed':
            recommendations = recommendations.filter(is_viewed=True)
        elif viewed == 'not_viewed':
            recommendations = recommendations.filter(is_viewed=False)

    # Lấy danh sách các chủ đề cho bộ lọc
    subjects = Subject.objects.all()

    context = {
        'recommendations': recommendations,
        'subjects': subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
        'selected_type': rec_type,
        'selected_viewed': viewed,
        'recommendation_types': ContentRecommendation.RECOMMENDATION_TYPES,
    }

    return render(request, 'personalization/content_recommendation/list.html', context)

@login_required
def content_recommendation_detail(request, recommendation_id):
    """Hiển thị chi tiết đề xuất nội dung"""
    recommendation = get_object_or_404(ContentRecommendation, id=recommendation_id, user=request.user)

    # Đánh dấu đã xem nếu chưa
    if not recommendation.is_viewed:
        recommendation.is_viewed = True
        recommendation.save()

        # Lưu tương tác người dùng
        UserInteraction.objects.create(
            user=request.user,
            interaction_type='view',
            content_type='recommendation',
            content_id=recommendation.id
        )

    context = {
        'recommendation': recommendation,
    }

    return render(request, 'personalization/content_recommendation/detail.html', context)

@login_required
def content_recommendation_feedback(request, recommendation_id):
    """Nhận phản hồi về đề xuất nội dung"""
    recommendation = get_object_or_404(ContentRecommendation, id=recommendation_id, user=request.user)

    if request.method == 'POST':
        is_helpful = request.POST.get('is_helpful') == 'true'
        recommendation.is_helpful = is_helpful
        recommendation.save()

        # Lưu tương tác người dùng
        UserInteraction.objects.create(
            user=request.user,
            interaction_type='rate',
            content_type='recommendation',
            content_id=recommendation.id,
            rating=5 if is_helpful else 1
        )

        messages.success(request, 'Cảm ơn bạn đã gửi phản hồi!')
        return redirect('content_recommendation_list')

    return redirect('content_recommendation_detail', recommendation_id=recommendation.id)

# API endpoints
@login_required
def get_topics_by_subject(request):
    """API lấy danh sách chủ đề con theo chủ đề"""
    subject_id = request.GET.get('subject_id')
    if not subject_id:
        return JsonResponse({'error': 'Chưa chọn chủ đề'}, status=400)

    topics = Topic.objects.filter(subject_id=subject_id).values('id', 'name')
    return JsonResponse({'topics': list(topics)})

@login_required
def dashboard(request):
    """Bảng điều khiển cá nhân hóa"""
    # Lấy thông tin lộ trình học tập
    active_pathways = LearningPathway.objects.filter(user=request.user, is_active=True).order_by('-created_at')[:5]

    # Lấy đề xuất nội dung mới nhất
    new_recommendations = ContentRecommendation.objects.filter(user=request.user, is_viewed=False).order_by('-relevance_score')[:5]

    # Lấy điểm mạnh và điểm yếu hàng đầu
    top_strengths = UserStrengthWeakness.objects.filter(user=request.user, is_strength=True).order_by('-proficiency_score')[:3]
    top_weaknesses = UserStrengthWeakness.objects.filter(user=request.user, is_strength=False).order_by('proficiency_score')[:3]

    # Lấy nhắc nhở học tập đang hoạt động
    active_reminders = StudyReminder.objects.filter(user=request.user, is_active=True).order_by('reminder_time')[:5]

    # Lấy hoặc tạo sở thích học tập và tùy chỉnh giao diện
    learning_preference, _ = LearningPreference.objects.get_or_create(user=request.user)
    ui_preference, _ = UIPreference.objects.get_or_create(user=request.user)

    context = {
        'active_pathways': active_pathways,
        'new_recommendations': new_recommendations,
        'top_strengths': top_strengths,
        'top_weaknesses': top_weaknesses,
        'active_reminders': active_reminders,
        'learning_preference': learning_preference,
        'ui_preference': ui_preference,
    }

    return render(request, 'personalization/dashboard.html', context)
