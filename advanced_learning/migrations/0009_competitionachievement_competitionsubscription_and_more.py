# Generated by Django 5.2 on 2025-04-08 17:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "advanced_learning",
            "0008_achievement_interactiveexercise_difficulty_level_and_more",
        ),
        ("content", "0002_alter_subject_icon"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CompetitionAchievement",
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
                    "requirement",
                    models.JSONField(help_text="Yêu cầu để đạt được thành tích"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="CompetitionSubscription",
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
                    "notification_type",
                    models.CharField(
                        choices=[
                            ("all", "Tất cả cuộc thi"),
                            ("subject", "Theo chủ đề"),
                            ("specific", "Cuộc thi cụ thể"),
                        ],
                        max_length=20,
                    ),
                ),
                ("email_notification", models.BooleanField(default=True)),
                ("push_notification", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="CompetitionTeam",
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
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                (
                    "logo",
                    models.ImageField(blank=True, null=True, upload_to="team_logos/"),
                ),
                ("score", models.PositiveIntegerField(default=0)),
                ("rank", models.PositiveIntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-score"],
            },
        ),
        migrations.CreateModel(
            name="LiveCompetition",
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
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("start_time", models.DateTimeField(blank=True, null=True)),
                ("end_time", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("waiting", "Chờ bắt đầu"),
                            ("active", "Đang diễn ra"),
                            ("completed", "Đã kết thúc"),
                            ("cancelled", "Đã hủy"),
                        ],
                        default="waiting",
                        max_length=20,
                    ),
                ),
                ("current_question_index", models.PositiveIntegerField(default=0)),
                ("max_participants", models.PositiveIntegerField(default=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="LiveParticipant",
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
                ("score", models.PositiveIntegerField(default=0)),
                ("rank", models.PositiveIntegerField(blank=True, null=True)),
                ("answers", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                ("last_activity", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name="competitionanswer",
            options={"ordering": ["order"]},
        ),
        migrations.AlterModelOptions(
            name="competitionmode",
            options={"ordering": ["-start_time"]},
        ),
        migrations.AddField(
            model_name="competitionanswer",
            name="explanation",
            field=models.TextField(blank=True, help_text="Giải thích cho đáp án này"),
        ),
        migrations.AddField(
            model_name="competitionanswer",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to="competition_answers/"
            ),
        ),
        migrations.AddField(
            model_name="competitionanswer",
            name="order",
            field=models.PositiveIntegerField(default=0, help_text="Thứ tự hiển thị"),
        ),
        migrations.AddField(
            model_name="competitionmode",
            name="competition_type",
            field=models.CharField(
                choices=[
                    ("individual", "Cá nhân"),
                    ("team", "Đồng đội"),
                    ("live", "Trực tiếp"),
                    ("realtime", "Thời gian thực"),
                ],
                default="individual",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="competitionmode",
            name="difficulty_level",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "Dễ"),
                    (2, "Trung bình"),
                    (3, "Khó"),
                    (4, "Rất khó"),
                    (5, "Chuyên gia"),
                ],
                default=2,
            ),
        ),
        migrations.AddField(
            model_name="competitionmode",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="competitions/"),
        ),
        migrations.AddField(
            model_name="competitionmode",
            name="is_featured",
            field=models.BooleanField(
                default=False, help_text="Đánh dấu cuộc thi nổi bật"
            ),
        ),
        migrations.AddField(
            model_name="competitionmode",
            name="lesson",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="competitions",
                to="content.lesson",
            ),
        ),
        migrations.AddField(
            model_name="competitionmode",
            name="points",
            field=models.PositiveIntegerField(
                default=100, help_text="Điểm thưởng khi hoàn thành cuộc thi"
            ),
        ),
        migrations.AddField(
            model_name="competitionparticipant",
            name="answers",
            field=models.JSONField(
                blank=True, default=dict, help_text="Các câu trả lời của người dùng"
            ),
        ),
        migrations.AddField(
            model_name="competitionparticipant",
            name="is_shared",
            field=models.BooleanField(default=False, help_text="Đã chia sẻ kết quả"),
        ),
        migrations.AddField(
            model_name="competitionparticipant",
            name="time_spent",
            field=models.PositiveIntegerField(
                default=0, help_text="Thời gian đã sử dụng (giây)"
            ),
        ),
        migrations.AddField(
            model_name="competitionquestion",
            name="code_template",
            field=models.TextField(
                blank=True, help_text="Mẫu mã cho câu hỏi lập trình"
            ),
        ),
        migrations.AddField(
            model_name="competitionquestion",
            name="difficulty_level",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "Dễ"),
                    (2, "Trung bình"),
                    (3, "Khó"),
                    (4, "Rất khó"),
                    (5, "Chuyên gia"),
                ],
                default=2,
            ),
        ),
        migrations.AddField(
            model_name="competitionquestion",
            name="explanation",
            field=models.TextField(blank=True, help_text="Giải thích cho đáp án đúng"),
        ),
        migrations.AddField(
            model_name="competitionquestion",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to="competition_questions/"
            ),
        ),
        migrations.AddField(
            model_name="competitionquestion",
            name="question_type",
            field=models.CharField(
                choices=[
                    ("multiple_choice", "Nhiều lựa chọn"),
                    ("single_choice", "Một lựa chọn"),
                    ("true_false", "Đúng/Sai"),
                    ("text", "Văn bản"),
                    ("code", "Mã lập trình"),
                ],
                default="single_choice",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="competitionquestion",
            name="test_cases",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Các trường hợp kiểm tra cho câu hỏi lập trình",
            ),
        ),
        migrations.AddField(
            model_name="competitionquestion",
            name="time_limit",
            field=models.PositiveIntegerField(
                default=30, help_text="Thời gian trả lời (giây)"
            ),
        ),
        migrations.AlterField(
            model_name="achievement",
            name="achievement_type",
            field=models.CharField(
                choices=[
                    ("exercise", "Hoàn thành bài tập"),
                    ("streak", "Chuỗi ngày liên tiếp"),
                    ("points", "Điểm số"),
                    ("completion", "Hoàn thành khóa học"),
                    ("special", "Thành tích đặc biệt"),
                    ("competition", "Cuộc thi đấu"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="competitionparticipant",
            unique_together={("user", "competition")},
        ),
        migrations.AddIndex(
            model_name="competitionanswer",
            index=models.Index(
                fields=["question", "is_correct"], name="advanced_le_questio_56960d_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="competitionmode",
            index=models.Index(
                fields=["start_time"], name="advanced_le_start_t_57d003_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="competitionmode",
            index=models.Index(
                fields=["end_time"], name="advanced_le_end_tim_adc586_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="competitionmode",
            index=models.Index(
                fields=["is_active"], name="advanced_le_is_acti_665c78_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="competitionmode",
            index=models.Index(
                fields=["competition_type"], name="advanced_le_competi_682e52_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="competitionquestion",
            index=models.Index(
                fields=["competition", "order"], name="advanced_le_competi_4b2135_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="competitionquestion",
            index=models.Index(
                fields=["question_type"], name="advanced_le_questio_4433d8_idx"
            ),
        ),
        migrations.AddField(
            model_name="competitionachievement",
            name="achievement",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="competitions",
                to="advanced_learning.achievement",
            ),
        ),
        migrations.AddField(
            model_name="competitionachievement",
            name="competition",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="achievements",
                to="advanced_learning.competitionmode",
            ),
        ),
        migrations.AddField(
            model_name="competitionsubscription",
            name="competition",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subscriptions",
                to="advanced_learning.competitionmode",
            ),
        ),
        migrations.AddField(
            model_name="competitionsubscription",
            name="subject",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="competition_subscriptions",
                to="content.subject",
            ),
        ),
        migrations.AddField(
            model_name="competitionsubscription",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="competition_subscriptions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="competitionteam",
            name="competition",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="teams",
                to="advanced_learning.competitionmode",
            ),
        ),
        migrations.AddField(
            model_name="competitionteam",
            name="leader",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="led_teams",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="competitionparticipant",
            name="team",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="members",
                to="advanced_learning.competitionteam",
            ),
        ),
        migrations.AddIndex(
            model_name="competitionparticipant",
            index=models.Index(
                fields=["user", "competition"], name="advanced_le_user_id_b8c23a_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="competitionparticipant",
            index=models.Index(
                fields=["competition", "score"], name="advanced_le_competi_45112b_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="competitionparticipant",
            index=models.Index(
                fields=["competition", "rank"], name="advanced_le_competi_443c47_idx"
            ),
        ),
        migrations.AddField(
            model_name="livecompetition",
            name="competition",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="live_sessions",
                to="advanced_learning.competitionmode",
            ),
        ),
        migrations.AddField(
            model_name="livecompetition",
            name="host",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="hosted_competitions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="liveparticipant",
            name="live_competition",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="participants",
                to="advanced_learning.livecompetition",
            ),
        ),
        migrations.AddField(
            model_name="liveparticipant",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="live_participations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="competitionachievement",
            unique_together={("competition", "achievement")},
        ),
        migrations.AlterUniqueTogether(
            name="competitionsubscription",
            unique_together={("user", "notification_type", "subject", "competition")},
        ),
        migrations.AlterUniqueTogether(
            name="competitionteam",
            unique_together={("name", "competition")},
        ),
        migrations.AlterUniqueTogether(
            name="liveparticipant",
            unique_together={("live_competition", "user")},
        ),
    ]
