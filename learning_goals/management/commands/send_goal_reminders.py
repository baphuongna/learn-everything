from django.core.management.base import BaseCommand
from django.utils import timezone
from learning_goals.models import LearningGoal

class Command(BaseCommand):
    help = 'Gửi nhắc nhở cho các mục tiêu học tập'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Bắt đầu gửi nhắc nhở cho các mục tiêu học tập...'))
        
        # Lấy tất cả các mục tiêu đang hoạt động
        active_goals = LearningGoal.objects.filter(
            status__in=['not_started', 'in_progress', 'overdue'],
            reminder_enabled=True
        )
        
        reminders_sent = 0
        
        for goal in active_goals:
            if goal.needs_reminder():
                goal.send_reminder()
                reminders_sent += 1
                self.stdout.write(self.style.SUCCESS(f'Đã gửi nhắc nhở cho mục tiêu: {goal.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'Hoàn thành! Đã gửi {reminders_sent} nhắc nhở.'))
