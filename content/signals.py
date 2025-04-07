from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Subject, Lesson
from utils.image_utils import ensure_subject_image, ensure_lesson_image

@receiver(post_save, sender=Subject)
def create_subject_image(sender, instance, created, **kwargs):
    """
    Tín hiệu để tự động tạo ảnh cho chủ đề nếu không có.
    """
    ensure_subject_image(instance)

@receiver(post_save, sender=Lesson)
def create_lesson_image(sender, instance, created, **kwargs):
    """
    Tín hiệu để tự động tạo ảnh cho bài học nếu không có.
    """
    ensure_lesson_image(instance)
