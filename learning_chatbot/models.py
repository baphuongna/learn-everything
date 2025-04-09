from django.db import models
from django.contrib.auth.models import User
from content.models import Subject, Topic, Lesson

class ChatbotCategory(models.Model):
    """Danh mục câu hỏi thường gặp"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Liên kết với nội dung học tập (tùy chọn)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='chatbot_categories')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='chatbot_categories')

    class Meta:
        verbose_name = 'Danh mục câu hỏi'
        verbose_name_plural = 'Danh mục câu hỏi'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class ChatbotQuestion(models.Model):
    """Câu hỏi thường gặp"""
    category = models.ForeignKey(ChatbotCategory, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    answer = models.TextField()
    keywords = models.CharField(max_length=255, blank=True, help_text='Các từ khóa, phân cách bằng dấu phẩy')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Liên kết với nội dung học tập (tùy chọn)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='chatbot_questions')

    class Meta:
        verbose_name = 'Câu hỏi'
        verbose_name_plural = 'Câu hỏi'
        ordering = ['category', 'order']

    def __str__(self):
        return self.question[:50]

    def get_keywords_list(self):
        """Trả về danh sách các từ khóa"""
        if not self.keywords:
            return []
        return [keyword.strip().lower() for keyword in self.keywords.split(',')]

class ChatbotConversation(models.Model):
    """Cuộc trò chuyện với chatbot"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatbot_conversations')
    session_id = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cuộc trò chuyện'
        verbose_name_plural = 'Cuộc trò chuyện'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Cuộc trò chuyện {self.id} - {self.user.username}"

class ChatbotMessage(models.Model):
    """Tin nhắn trong cuộc trò chuyện với chatbot"""
    ROLE_CHOICES = [
        ('user', 'Người dùng'),
        ('bot', 'Chatbot')
    ]

    conversation = models.ForeignKey(ChatbotConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Liên kết với câu hỏi thường gặp (nếu có)
    matched_question = models.ForeignKey(ChatbotQuestion, on_delete=models.SET_NULL, null=True, blank=True, related_name='matched_messages')

    class Meta:
        verbose_name = 'Tin nhắn'
        verbose_name_plural = 'Tin nhắn'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"

class ChatbotFeedback(models.Model):
    """Phản hồi về câu trả lời của chatbot"""
    RATING_CHOICES = [
        (1, 'Rất không hài lòng'),
        (2, 'Không hài lòng'),
        (3, 'Bình thường'),
        (4, 'Hài lòng'),
        (5, 'Rất hài lòng')
    ]

    message = models.ForeignKey(ChatbotMessage, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatbot_feedback')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Phản hồi'
        verbose_name_plural = 'Phản hồi'
        ordering = ['-created_at']

    def __str__(self):
        return f"Phản hồi từ {self.user.username}: {self.rating}/5"