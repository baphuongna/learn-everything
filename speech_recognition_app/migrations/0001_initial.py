# Generated by Django 5.2 on 2025-04-09 17:53

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SpeechRecognitionResult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "audio_file",
                    models.FileField(
                        blank=True, null=True, upload_to="speech_recognition/"
                    ),
                ),
                ("text_result", models.TextField()),
                (
                    "expected_text",
                    models.TextField(
                        blank=True,
                        help_text="Văn bản mẫu để so sánh với kết quả nhận diện",
                        null=True,
                    ),
                ),
                ("language", models.CharField(default="vi-VN", max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "pronunciation_score",
                    models.FloatField(
                        blank=True,
                        help_text="Điểm đánh giá phát âm (0-100)",
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                    ),
                ),
                (
                    "accuracy_score",
                    models.FloatField(
                        blank=True,
                        help_text="Điểm chính xác về nội dung (0-100)",
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                    ),
                ),
                (
                    "fluency_score",
                    models.FloatField(
                        blank=True,
                        help_text="Điểm trôi chảy (0-100)",
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                    ),
                ),
                (
                    "feedback",
                    models.TextField(
                        blank=True, help_text="Phản hồi chi tiết về phát âm", null=True
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="speech_recognition_results",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Kết quả nhận diện giọng nói",
                "verbose_name_plural": "Kết quả nhận diện giọng nói",
                "ordering": ["-created_at"],
            },
        ),
    ]
