from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from content.models import Subject

class MemoryCategory(models.Model):
    """Danh mục phân loại các ghi nhớ"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memory_categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='memory_categories')
    slug = models.SlugField(max_length=100)
    color = models.CharField(max_length=20, default='#007bff')  # Màu sắc hiển thị
    icon = models.CharField(max_length=50, default='fas fa-folder')  # Icon Font Awesome
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Memory categories'
        ordering = ['name']
        unique_together = ['user', 'slug']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('memory_category_detail', kwargs={'slug': self.slug})

class MemoryItem(models.Model):
    """Các ghi nhớ của người dùng"""
    PRIORITY_CHOICES = [
        (1, 'Thấp'),
        (2, 'Trung bình'),
        (3, 'Cao')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memory_items')
    category = models.ForeignKey(MemoryCategory, on_delete=models.CASCADE, related_name='memory_items')
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=1)
    is_favorite = models.BooleanField(default=False)
    tags = models.CharField(max_length=200, blank=True, help_text='Các thẻ phân cách bằng dấu phẩy')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Trường cho Spaced Repetition
    next_review_date = models.DateTimeField(null=True, blank=True)
    review_count = models.PositiveIntegerField(default=0)
    last_review_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('memory_item_detail', kwargs={'pk': self.pk})

    def get_tags_list(self):
        """Trả về danh sách các thẻ"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

class MemoryAttachment(models.Model):
    """Tập tin đính kèm cho ghi nhớ"""
    memory_item = models.ForeignKey(MemoryItem, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='memory_attachments/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name
