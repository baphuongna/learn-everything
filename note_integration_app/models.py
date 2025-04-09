from django.db import models
from django.contrib.auth.models import User


class NoteIntegrationAccount(models.Model):
    """Lưu trữ thông tin tài khoản tích hợp với các công cụ ghi chú"""
    
    PROVIDER_CHOICES = [
        ('notion', 'Notion'),
        ('evernote', 'Evernote'),
        ('onenote', 'Microsoft OneNote'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_integration_accounts')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    account_info = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'provider')
        verbose_name = 'Tài khoản tích hợp ghi chú'
        verbose_name_plural = 'Tài khoản tích hợp ghi chú'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_provider_display()}"


class SyncedNote(models.Model):
    """Lưu trữ thông tin về các ghi chú đã đồng bộ"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='synced_notes')
    integration_account = models.ForeignKey(NoteIntegrationAccount, on_delete=models.CASCADE, related_name='synced_notes')
    
    # Thông tin về ghi chú trong hệ thống
    memory_item_id = models.IntegerField(blank=True, null=True)  # ID của ghi chú trong Memory Bank
    
    # Thông tin về ghi chú trong dịch vụ bên ngoài
    external_id = models.CharField(max_length=255)  # ID của ghi chú trong dịch vụ bên ngoài
    external_url = models.URLField(blank=True, null=True)  # URL của ghi chú trong dịch vụ bên ngoài
    
    title = models.CharField(max_length=255)
    last_synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ghi chú đã đồng bộ'
        verbose_name_plural = 'Ghi chú đã đồng bộ'
    
    def __str__(self):
        return f"{self.title} ({self.integration_account.get_provider_display()})"
