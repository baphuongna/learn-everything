from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile
from utils.image_utils import ensure_profile_image

@receiver(post_save, sender=UserProfile)
def create_profile_image(sender, instance, created, **kwargs):
    """
    Tín hiệu để tự động tạo ảnh cho hồ sơ người dùng nếu không có.
    """
    ensure_profile_image(instance)
