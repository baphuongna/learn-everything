from django.db import models
from django.contrib.auth.models import User
from content.models import Subject, Topic, Lesson

class AIAssistantChat(models.Model):
    """Lưu trữ cuộc trò chuyện với trợ lý AI"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_chats')
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Liên kết với nội dung học tập (tùy chọn)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_chats')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_chats')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_chats')

    def __str__(self):
        return f"{self.title or 'Cuộc trò chuyện'} - {self.user.username}"

class AIAssistantMessage(models.Model):
    """Lưu trữ tin nhắn trong cuộc trò chuyện với trợ lý AI"""
    ROLE_CHOICES = [
        ('user', 'Người dùng'),
        ('assistant', 'Trợ lý AI'),
        ('system', 'Hệ thống')
    ]

    chat = models.ForeignKey(AIAssistantChat, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."

class AIAssistantFeedback(models.Model):
    """Lưu trữ phản hồi của người dùng về câu trả lời của trợ lý AI"""
    RATING_CHOICES = [
        (1, 'Rất không hài lòng'),
        (2, 'Không hài lòng'),
        (3, 'Bình thường'),
        (4, 'Hài lòng'),
        (5, 'Rất hài lòng')
    ]

    message = models.ForeignKey(AIAssistantMessage, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_feedback')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Phản hồi từ {self.user.username}: {self.rating}/5"

class AIAssistantPrompt(models.Model):
    """Lưu trữ các prompt mẫu cho trợ lý AI"""
    PROMPT_TYPES = [
        ('system', 'Hệ thống'),
        ('subject', 'Chủ đề'),
        ('topic', 'Chủ đề con'),
        ('lesson', 'Bài học'),
        ('general', 'Chung')
    ]

    name = models.CharField(max_length=200)
    prompt_type = models.CharField(max_length=10, choices=PROMPT_TYPES)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Liên kết với nội dung học tập (tùy chọn)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_prompts')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_prompts')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_prompts')

    def __str__(self):
        return self.name