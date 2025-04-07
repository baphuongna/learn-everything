from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Flashcard
from utils.image_utils import ensure_flashcard_image

@receiver(post_save, sender=Flashcard)
def create_flashcard_image(sender, instance, created, **kwargs):
    """
    Tín hiệu để tự động tạo ảnh cho flashcard nếu không có.
    """
    ensure_flashcard_image(instance)
