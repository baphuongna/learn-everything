from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Subject(models.Model):
    """Chủ đề học tập (Tiếng Anh, Python, v.v.)"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='subject_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('subject_detail', kwargs={'slug': self.slug})

class Topic(models.Model):
    """Chủ đề con trong mỗi Subject"""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['subject', 'order']
        unique_together = ['subject', 'slug']

    def __str__(self):
        return f"{self.subject.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('topic_detail', kwargs={'subject_slug': self.subject.slug, 'topic_slug': self.slug})

class Lesson(models.Model):
    """Bài học cụ thể trong mỗi Topic"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    slug = models.SlugField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    video_url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='lesson_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['topic', 'order']
        unique_together = ['topic', 'slug']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('lesson_detail', kwargs={
            'subject_slug': self.topic.subject.slug,
            'topic_slug': self.topic.slug,
            'lesson_slug': self.slug
        })
