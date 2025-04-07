from django.db import models
from django.contrib.auth.models import User
from content.models import Lesson

class FlashcardSet(models.Model):
    """Tập hợp flashcard, liên kết với Lesson"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='flashcard_sets')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

class Flashcard(models.Model):
    """Card cá nhân, có mặt trước (front) và mặt sau (back)"""
    flashcard_set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE, related_name='flashcards')
    front = models.TextField()
    back = models.TextField()
    image = models.ImageField(upload_to='flashcard_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.front

class SpacedRepetitionSchedule(models.Model):
    """Lịch ôn tập theo phương pháp Spaced Repetition"""
    RECALL_LEVEL_CHOICES = [
        (1, 'Khó nhớ'),
        (2, 'Nhớ mờ mờ'),
        (3, 'Nhớ rõ')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spaced_repetition_schedules')
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name='spaced_repetition_schedules')
    next_review_date = models.DateTimeField()
    recall_level = models.IntegerField(choices=RECALL_LEVEL_CHOICES, default=1)
    review_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'flashcard']

    def __str__(self):
        return f"{self.user.username} - {self.flashcard.front} - Level {self.recall_level}"
