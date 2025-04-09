from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class SpeechRecognitionResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='speech_recognition_results')
    audio_file = models.FileField(upload_to='speech_recognition/', null=True, blank=True)
    text_result = models.TextField()
    expected_text = models.TextField(blank=True, null=True, help_text='Văn bản mẫu để so sánh với kết quả nhận diện')
    language = models.CharField(max_length=10, default='vi-VN')
    created_at = models.DateTimeField(auto_now_add=True)

    # Các trường đánh giá phát âm
    pronunciation_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text='Điểm đánh giá phát âm (0-100)')
    accuracy_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text='Điểm chính xác về nội dung (0-100)')
    fluency_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text='Điểm trôi chảy (0-100)')
    feedback = models.TextField(blank=True, null=True, help_text='Phản hồi chi tiết về phát âm')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Kết quả nhận diện giọng nói'
        verbose_name_plural = 'Kết quả nhận diện giọng nói'

    def __str__(self):
        return f"Kết quả nhận diện của {self.user.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    def get_overall_score(self):
        """Tính điểm tổng hợp từ các điểm thành phần"""
        scores = [s for s in [self.pronunciation_score, self.accuracy_score, self.fluency_score] if s is not None]
        if not scores:
            return None
        return sum(scores) / len(scores)
