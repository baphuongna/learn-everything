# Generated by Django 5.2 on 2025-04-10 08:53

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advanced_learning', '0009_competitionachievement_competitionsubscription_and_more'),
        ('content', '0002_alter_subject_icon'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='userproject',
            name='completed_tasks',
            field=models.JSONField(blank=True, default=list, help_text='Danh sách ID các task đã hoàn thành', null=True),
        ),
        migrations.CreateModel(
            name='LearningGoal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('goal_type', models.CharField(choices=[('daily', 'Hàng ngày'), ('weekly', 'Hàng tuần'), ('monthly', 'Hàng tháng'), ('custom', 'Tùy chỉnh')], default='daily', max_length=20)),
                ('goal_metric', models.CharField(choices=[('study_time', 'Thời gian học tập (phút)'), ('notes_count', 'Số ghi chú'), ('mindmaps_count', 'Số mind map'), ('projects_progress', 'Tiến độ dự án (%)'), ('exercises_completed', 'Số bài tập hoàn thành'), ('competition_points', 'Điểm thi đấu'), ('custom', 'Tùy chỉnh')], default='study_time', max_length=20)),
                ('target_value', models.PositiveIntegerField(help_text='Giá trị mục tiêu')),
                ('current_value', models.PositiveIntegerField(default=0, help_text='Giá trị hiện tại')),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='advanced_learning_goals', to='content.subject')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='advanced_learning_goals', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DailyStudyLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('total_minutes', models.PositiveIntegerField(default=0, help_text='Tổng số phút học tập')),
                ('pomodoro_count', models.PositiveIntegerField(default=0, help_text='Số pomodoro hoàn thành')),
                ('notes_created', models.PositiveIntegerField(default=0, help_text='Số ghi chú đã tạo')),
                ('exercises_completed', models.PositiveIntegerField(default=0, help_text='Số bài tập đã hoàn thành')),
                ('competitions_participated', models.PositiveIntegerField(default=0, help_text='Số cuộc thi đã tham gia')),
                ('competition_points', models.PositiveIntegerField(default=0, help_text='Điểm thi đấu đã kiếm được')),
                ('subjects_studied', models.JSONField(default=dict, help_text='Các môn học đã học và thời gian tương ứng')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='study_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
                'unique_together': {('user', 'date')},
            },
        ),
    ]
