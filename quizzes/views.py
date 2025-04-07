from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from .models import Quiz, Question, Answer, QuizAttempt, UserAnswer

def quiz_list(request):
    """Hiển thị danh sách các bài kiểm tra"""
    quizzes = Quiz.objects.all().select_related('lesson__topic__subject')
    return render(request, 'quizzes/quiz_list.html', {'quizzes': quizzes})

def quiz_detail(request, quiz_id):
    """Hiển thị chi tiết bài kiểm tra"""
    quiz = get_object_or_404(Quiz, id=quiz_id)

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

    return render(request, 'quizzes/quiz_detail.html', context)

@login_required
def start_quiz(request, quiz_id):
    """Bắt đầu làm bài kiểm tra"""
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Lưu trạng thái bắt đầu làm bài vào session
    request.session['quiz_started'] = quiz_id
    request.session['quiz_start_time'] = timezone.now().isoformat()

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

        return redirect('quiz_result', attempt_id=quiz_attempt.id)

    return redirect('quiz_detail', quiz_id=quiz_id)

@login_required
def quiz_result(request, attempt_id):
    """Hiển thị kết quả bài kiểm tra"""
    quiz_attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    user_answers = UserAnswer.objects.filter(quiz_attempt=quiz_attempt).select_related('question').prefetch_related('selected_answers')

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

    return render(request, 'quizzes/quiz_result.html', context)
