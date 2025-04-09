from django.db import models
from django.contrib.auth.models import User


class OCRResult(models.Model):
    """Lưu trữ kết quả nhận dạng ký tự quang học (OCR)"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ocr_results')
    image = models.ImageField(upload_to='ocr_images/')
    text_result = models.TextField()
    language = models.CharField(max_length=10, default='vie')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Kết quả OCR'
        verbose_name_plural = 'Kết quả OCR'
    
    def __str__(self):
        return f"OCR của {self.user.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
