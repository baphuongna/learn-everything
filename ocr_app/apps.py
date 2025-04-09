from django.apps import AppConfig


class OcrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ocr_app'
    verbose_name = 'Nhận dạng ký tự quang học (OCR)'
