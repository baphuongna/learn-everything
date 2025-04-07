from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from content.models import Lesson, Subject

class UserProfile(models.Model):
    """Thông tin bổ sung của người dùng"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    preferred_subjects = models.ManyToManyField(Subject, blank=True, related_name='interested_users')
    daily_goal_minutes = models.PositiveIntegerField(default=30, help_text='Mục tiêu học tập hàng ngày tính bằng phút')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Tạo UserProfile khi User được tạo"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Lưu UserProfile khi User được lưu"""
    instance.profile.save()

class UserProgress(models.Model):
    """Theo dõi tiến độ học của người dùng"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(blank=True, null=True)
    last_accessed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'lesson']
        verbose_name_plural = 'User progress'

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} - {'Hoàn thành' if self.completed else 'Chưa hoàn thành'}"

class StudySession(models.Model):
    """Ghi lại các phiên học tập của người dùng"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.user.username} - {self.subject.name if self.subject else 'Không xác định'} - {self.duration_minutes} phút"
