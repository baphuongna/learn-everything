from django.db import models
from django.contrib.auth.models import User
from content.models import Lesson

class Quiz(models.Model):
    """Bộ câu hỏi trắc nghiệm, liên kết với Lesson"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    time_limit = models.PositiveIntegerField(help_text='Thời gian làm bài tính bằng phút', blank=True, null=True)
    pass_score = models.PositiveIntegerField(default=70, help_text='Điểm đậu tính theo phần trăm')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

class Question(models.Model):
    """Câu hỏi trong quiz"""
    QUESTION_TYPES = [
        ('single', 'Chọn một đáp án'),
        ('multiple', 'Chọn nhiều đáp án'),
        ('text', 'Trả lời văn bản')
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='single')
    explanation = models.TextField(blank=True, help_text='Giải thích đáp án')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['quiz', 'order']

    def __str__(self):
        return self.question_text[:50]

class Answer(models.Model):
    """Các đáp án cho câu hỏi"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.answer_text[:30]} - {'\u0110úng' if self.is_correct else 'Sai'}"

class QuizAttempt(models.Model):
    """Lưu lại các lần làm quiz của người dùng"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.FloatField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    passed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}%"

class UserAnswer(models.Model):
    """Lưu lại câu trả lời của người dùng cho mỗi câu hỏi"""
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answers = models.ManyToManyField(Answer, blank=True)
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quiz_attempt.user.username} - {self.question.question_text[:30]}"
