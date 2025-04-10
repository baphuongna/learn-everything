# Generated by Django 5.2 on 2025-04-10 09:53

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_goals', '0003_learninggoal_is_recurring_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='learninggoal',
            name='last_reminder_sent',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Lần nhắc nhở gần nhất'),
        ),
        migrations.AddField(
            model_name='learninggoal',
            name='reminder_app',
            field=models.BooleanField(default=True, verbose_name='Gửi nhắc nhở trong ứng dụng'),
        ),
        migrations.AddField(
            model_name='learninggoal',
            name='reminder_days_before',
            field=models.PositiveIntegerField(default=1, verbose_name='Số ngày nhắc trước hạn'),
        ),
        migrations.AddField(
            model_name='learninggoal',
            name='reminder_email',
            field=models.BooleanField(default=True, verbose_name='Gửi nhắc nhở qua email'),
        ),
        migrations.AddField(
            model_name='learninggoal',
            name='reminder_time',
            field=models.TimeField(default=django.utils.timezone.now, verbose_name='Thời gian nhắc nhở'),
        ),
    ]
