from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
from datetime import timedelta
import json
from .models import FlashcardSet, Flashcard, SpacedRepetitionSchedule

def flashcard_list(request):
    """Hiển thị danh sách các bộ flashcard"""
    flashcard_sets = FlashcardSet.objects.all().select_related('lesson__topic__subject')
    return render(request, 'flashcards/flashcard_list.html', {'flashcard_sets': flashcard_sets})

def flashcard_set_detail(request, flashcard_set_id):
    """Hiển thị chi tiết bộ flashcard và các flashcard trong bộ"""
    flashcard_set = get_object_or_404(FlashcardSet, id=flashcard_set_id)
    flashcards = flashcard_set.flashcards.all()

    # Tính toán tiến độ ôn tập nếu người dùng đã đăng nhập
    mastered_count = 0
    mastered_percentage = 0

    if request.user.is_authenticated and flashcards.exists():
        # Đếm số flashcard đã thuộc (recall_level = 3)
        mastered_count = SpacedRepetitionSchedule.objects.filter(
            user=request.user,
            flashcard__in=flashcards,
            recall_level=3
        ).count()

        # Tính phần trăm đã thuộc
        mastered_percentage = int((mastered_count / flashcards.count()) * 100)

    context = {
        'flashcard_set': flashcard_set,
        'flashcards': flashcards,
        'mastered_count': mastered_count,
        'mastered_percentage': mastered_percentage
    }

    return render(request, 'flashcards/flashcard_set_detail.html', context)

@login_required
def update_recall_level(request):
    """Cập nhật mức độ nhớ của flashcard và lên lịch ôn tập tiếp theo"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            flashcard_id = data.get('flashcard_id')
            recall_level = int(data.get('recall_level'))

            if not flashcard_id or recall_level not in [1, 2, 3]:
                return JsonResponse({'success': False, 'error': 'Dữ liệu không hợp lệ'})

            flashcard = get_object_or_404(Flashcard, id=flashcard_id)

            # Tính ngày ôn tập tiếp theo dựa trên mức độ nhớ
            now = timezone.now()
            if recall_level == 1:  # Khó nhớ
                next_review_date = now + timedelta(days=1)
            elif recall_level == 2:  # Nhớ mờ mờ
                next_review_date = now + timedelta(days=3)
            else:  # Nhớ rõ
                next_review_date = now + timedelta(days=7)

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

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Phương thức không được hỗ trợ'})

@login_required
def due_flashcards(request):
    """Hiển thị các flashcard cần ôn tập hôm nay"""
    today = timezone.now()
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

    return render(request, 'flashcards/due_flashcards.html', context)
