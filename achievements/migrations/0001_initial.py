# Generated by Django 5.2 on 2025-04-08 10:52

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Tên huy hiệu')),
                ('description', models.TextField(verbose_name='Mô tả')),
                ('category', models.CharField(choices=[('learning', 'Học tập'), ('goals', 'Mục tiêu'), ('flashcards', 'Flashcards'), ('quizzes', 'Bài kiểm tra'), ('projects', 'Dự án'), ('special', 'Đặc biệt')], default='learning', max_length=20, verbose_name='Danh mục')),
                ('level', models.CharField(choices=[('bronze', 'Đồng'), ('silver', 'Bạc'), ('gold', 'Vàng'), ('platinum', 'Bạch kim')], default='bronze', max_length=20, verbose_name='Cấp độ')),
                ('icon', models.CharField(default='fa-award', max_length=50, verbose_name='Biểu tượng')),
                ('points', models.PositiveIntegerField(default=10, verbose_name='Điểm thưởng')),
                ('condition_type', models.CharField(max_length=100, verbose_name='Loại điều kiện')),
                ('condition_value', models.PositiveIntegerField(default=1, verbose_name='Giá trị điều kiện')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Huy hiệu',
                'verbose_name_plural': 'Huy hiệu',
                'ordering': ['category', 'level', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Tên phần thưởng')),
                ('description', models.TextField(verbose_name='Mô tả')),
                ('points_required', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Điểm yêu cầu')),
                ('icon', models.CharField(default='fa-gift', max_length=50, verbose_name='Biểu tượng')),
                ('is_active', models.BooleanField(default=True, verbose_name='Đang hoạt động')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Phần thưởng',
                'verbose_name_plural': 'Phần thưởng',
                'ordering': ['points_required', 'name'],
            },
        ),
        migrations.CreateModel(
            name='PointHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.PositiveIntegerField(verbose_name='Số điểm')),
                ('action_type', models.CharField(choices=[('earn', 'Nhận điểm'), ('use', 'Sử dụng điểm')], max_length=10, verbose_name='Loại hành động')),
                ('reason', models.CharField(max_length=255, verbose_name='Lý do')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='point_history', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Lịch sử điểm thưởng',
                'verbose_name_plural': 'Lịch sử điểm thưởng',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='RewardPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.PositiveIntegerField(default=0, verbose_name='Điểm thưởng')),
                ('lifetime_points', models.PositiveIntegerField(default=0, verbose_name='Tổng điểm thưởng')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='reward_points', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Điểm thưởng',
                'verbose_name_plural': 'Điểm thưởng',
            },
        ),
        migrations.CreateModel(
            name='UserReward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('redeemed_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_used', models.BooleanField(default=False, verbose_name='Đã sử dụng')),
                ('used_at', models.DateTimeField(blank=True, null=True, verbose_name='Thời gian sử dụng')),
                ('reward', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_rewards', to='achievements.reward')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rewards', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Phần thưởng người dùng',
                'verbose_name_plural': 'Phần thưởng người dùng',
                'ordering': ['-redeemed_at'],
            },
        ),
        migrations.CreateModel(
            name='UserBadge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('earned_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('badge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_badges', to='achievements.badge')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='badges', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Huy hiệu người dùng',
                'verbose_name_plural': 'Huy hiệu người dùng',
                'ordering': ['-earned_at'],
                'unique_together': {('user', 'badge')},
            },
        ),
    ]
