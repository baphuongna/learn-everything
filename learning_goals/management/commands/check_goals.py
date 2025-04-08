from django.core.management.base import BaseCommand
from django.utils import timezone
from learning_goals.tasks import check_goal_progress, check_inactive_goals

class Command(BaseCommand):
    help = 'Kiểm tra tiến độ mục tiêu và gửi thông báo nhắc nhở'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Bắt đầu kiểm tra tiến độ mục tiêu...'))
        
        # Kiểm tra tiến độ mục tiêu
        check_goal_progress()
        
        # Kiểm tra các mục tiêu không hoạt động
        check_inactive_goals()
        
        self.stdout.write(self.style.SUCCESS('Hoàn thành kiểm tra tiến độ mục tiêu!'))
