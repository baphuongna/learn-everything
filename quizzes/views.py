from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.urls import reverse
from .models import Quiz, Question, Answer, QuizAttempt, UserAnswer

def quiz_list(request):
    """Hiển thị danh sách các bài kiểm tra"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    difficulty = request.GET.get('difficulty', '')
    format_type = request.GET.get('format', '')

    # Lấy danh sách quiz
    quizzes = Quiz.objects.all().select_related('lesson__topic__subject')

    # Áp dụng bộ lọc
    if search_query:
        quizzes = quizzes.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(lesson__title__icontains=search_query) |
            Q(lesson__topic__name__icontains=search_query) |
            Q(lesson__topic__subject__name__icontains=search_query)
        )

    if subject_id:
        quizzes = quizzes.filter(lesson__topic__subject_id=subject_id)

    if difficulty:
        quizzes = quizzes.filter(difficulty_level=difficulty)

    # Lấy danh sách các chủ đề cho bộ lọc
    from content.models import Subject
    subjects = Subject.objects.all()

    context = {
        'quizzes': quizzes,
        'subjects': subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
        'selected_difficulty': difficulty,
        'difficulty_levels': Quiz.DIFFICULTY_LEVELS,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'quizzes/quiz_list_partial.html', context)

    return render(request, 'quizzes/quiz_list.html', context)

def quiz_detail(request, quiz_id):
    """Hiển thị chi tiết bài kiểm tra"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    format_type = request.GET.get('format', '')

    # Kiểm tra xem người dùng đã bắt đầu làm bài chưa
    quiz_started = False
    start_time = None
    questions = None

    if 'quiz_started' in request.session and request.session['quiz_started'] == quiz_id:
        quiz_started = True
        start_time = request.session.get('quiz_start_time')
        questions = quiz.questions.all().prefetch_related('answers')

    # Lấy các lần làm trước đó của người dùng
    previous_attempts = []
    if request.user.is_authenticated:
        previous_attempts = QuizAttempt.objects.filter(
            user=request.user,
            quiz=quiz
        ).order_by('-created_at')[:5]

    context = {
        'quiz': quiz,
        'quiz_started': quiz_started,
        'start_time': start_time,
        'questions': questions,
        'previous_attempts': previous_attempts
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'quizzes/quiz_detail_partial.html', context)

    return render(request, 'quizzes/quiz_detail.html', context)

@login_required
def start_quiz(request, quiz_id):
    """Bắt đầu làm bài kiểm tra"""
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Lưu trạng thái bắt đầu làm bài vào session
    request.session['quiz_started'] = quiz_id
    request.session['quiz_start_time'] = timezone.now().isoformat()

    # Kiểm tra nếu là request HTMX
    if request.htmx:
        # Trả về redirect thông qua header HX-Redirect
        response = render(request, 'quizzes/empty.html')
        response['HX-Redirect'] = request.build_absolute_uri(reverse('quiz_detail', args=[quiz_id]))
        return response

    return redirect('quiz_detail', quiz_id=quiz_id)

@login_required
def submit_quiz(request, quiz_id):
    """Nộp bài kiểm tra"""
    if request.method == 'POST':
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = quiz.questions.all().prefetch_related('answers')

        # Lấy thời gian bắt đầu và kết thúc
        start_time = timezone.datetime.fromisoformat(request.POST.get('start_time'))
        end_time = timezone.now()

        # Tạo bản ghi QuizAttempt
        quiz_attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            start_time=start_time,
            end_time=end_time,
            score=0  # Sẽ cập nhật sau
        )

        # Xử lý câu trả lời của người dùng
        correct_count = 0

        for question in questions:
            is_correct = False

            if question.question_type == 'text':
                # Xử lý câu hỏi dạng văn bản
                text_answer = request.POST.get(f'question_{question.id}_text', '')
                user_answer = UserAnswer.objects.create(
                    quiz_attempt=quiz_attempt,
                    question=question,
                    text_answer=text_answer,
                    is_correct=False  # Đánh giá thủ công sau
                )
            else:
                # Xử lý câu hỏi dạng chọn đáp án
                selected_answer_ids = request.POST.getlist(f'question_{question.id}')

                if not selected_answer_ids:
                    # Không chọn đáp án nào
                    user_answer = UserAnswer.objects.create(
                        quiz_attempt=quiz_attempt,
                        question=question,
                        is_correct=False
                    )
                else:
                    # Tạo UserAnswer
                    user_answer = UserAnswer.objects.create(
                        quiz_attempt=quiz_attempt,
                        question=question,
                        is_correct=False  # Sẽ cập nhật sau
                    )

                    # Thêm các đáp án đã chọn
                    selected_answers = Answer.objects.filter(id__in=selected_answer_ids)
                    user_answer.selected_answers.set(selected_answers)

                    # Kiểm tra đáp án
                    if question.question_type == 'single':
                        # Đúng khi chọn đúng 1 đáp án
                        if len(selected_answers) == 1 and selected_answers[0].is_correct:
                            is_correct = True
                    else:  # multiple
                        # Đúng khi chọn tất cả đáp án đúng và không chọn đáp án sai
                        correct_answers = Answer.objects.filter(question=question, is_correct=True)
                        if set(selected_answers) == set(correct_answers):
                            is_correct = True

            # Cập nhật trạng thái đúng/sai
            user_answer.is_correct = is_correct
            user_answer.save()

            if is_correct:
                correct_count += 1

        # Tính điểm số
        total_questions = questions.count()
        if total_questions > 0:
            score = (correct_count / total_questions) * 100
            quiz_attempt.score = score
            quiz_attempt.passed = score >= quiz.pass_score
            quiz_attempt.save()

        # Xóa trạng thái làm bài khỏi session
        if 'quiz_started' in request.session:
            del request.session['quiz_started']
        if 'quiz_start_time' in request.session:
            del request.session['quiz_start_time']

        # Kiểm tra nếu là request HTMX
        if request.htmx:
            # Trả về redirect thông qua header HX-Redirect
            response = render(request, 'quizzes/empty.html')
            response['HX-Redirect'] = request.build_absolute_uri(reverse('quiz_result', args=[quiz_attempt.id]))
            return response

        return redirect('quiz_result', attempt_id=quiz_attempt.id)

    return redirect('quiz_detail', quiz_id=quiz_id)

@login_required
def quiz_result(request, attempt_id):
    """Hiển thị kết quả bài kiểm tra"""
    quiz_attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    user_answers = UserAnswer.objects.filter(quiz_attempt=quiz_attempt).select_related('question').prefetch_related('selected_answers')
    format_type = request.GET.get('format', '')

    # Tính thời gian làm bài
    duration = (quiz_attempt.end_time - quiz_attempt.start_time).total_seconds() / 60

    # Đếm số câu đúng/sai
    correct_count = user_answers.filter(is_correct=True).count()
    incorrect_count = user_answers.count() - correct_count

    context = {
        'quiz_attempt': quiz_attempt,
        'user_answers': user_answers,
        'duration': round(duration, 1),
        'correct_count': correct_count,
        'incorrect_count': incorrect_count
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'quizzes/quiz_result_partial.html', context)

    return render(request, 'quizzes/quiz_result.html', context)
