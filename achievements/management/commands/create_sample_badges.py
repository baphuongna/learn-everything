from django.core.management.base import BaseCommand
from django.utils import timezone
from achievements.models import Badge, Reward

class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho hệ thống thành tích và phần thưởng'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Bắt đầu tạo dữ liệu mẫu...'))
        
        # Tạo các huy hiệu mẫu
        self.create_sample_badges()
        
        # Tạo các phần thưởng mẫu
        self.create_sample_rewards()
        
        self.stdout.write(self.style.SUCCESS('Hoàn thành tạo dữ liệu mẫu!'))
    
    def create_sample_badges(self):
        """Tạo các huy hiệu mẫu"""
        # Huy hiệu học tập
        learning_badges = [
            {
                'name': 'Người học mới',
                'description': 'Hoàn thành bài học đầu tiên',
                'category': 'learning',
                'level': 'bronze',
                'icon': 'fa-book-reader',
                'points': 10,
                'condition_type': 'lessons_completed',
                'condition_value': 1
            },
            {
                'name': 'Học sinh chăm chỉ',
                'description': 'Hoàn thành 10 bài học',
                'category': 'learning',
                'level': 'silver',
                'icon': 'fa-book-reader',
                'points': 50,
                'condition_type': 'lessons_completed',
                'condition_value': 10
            },
            {
                'name': 'Học giả',
                'description': 'Hoàn thành 50 bài học',
                'category': 'learning',
                'level': 'gold',
                'icon': 'fa-book-reader',
                'points': 200,
                'condition_type': 'lessons_completed',
                'condition_value': 50
            },
            {
                'name': 'Bậc thầy kiến thức',
                'description': 'Hoàn thành 100 bài học',
                'category': 'learning',
                'level': 'platinum',
                'icon': 'fa-book-reader',
                'points': 500,
                'condition_type': 'lessons_completed',
                'condition_value': 100
            },
        ]
        
        # Huy hiệu flashcards
        flashcard_badges = [
            {
                'name': 'Người ghi nhớ',
                'description': 'Ôn tập 10 flashcard',
                'category': 'flashcards',
                'level': 'bronze',
                'icon': 'fa-clone',
                'points': 10,
                'condition_type': 'flashcards_reviewed',
                'condition_value': 10
            },
            {
                'name': 'Trí nhớ tốt',
                'description': 'Ôn tập 50 flashcard',
                'category': 'flashcards',
                'level': 'silver',
                'icon': 'fa-clone',
                'points': 50,
                'condition_type': 'flashcards_reviewed',
                'condition_value': 50
            },
            {
                'name': 'Trí nhớ siêu phàm',
                'description': 'Ôn tập 200 flashcard',
                'category': 'flashcards',
                'level': 'gold',
                'icon': 'fa-clone',
                'points': 200,
                'condition_type': 'flashcards_reviewed',
                'condition_value': 200
            },
        ]
        
        # Huy hiệu mục tiêu
        goal_badges = [
            {
                'name': 'Người đặt mục tiêu',
                'description': 'Tạo mục tiêu học tập đầu tiên',
                'category': 'goals',
                'level': 'bronze',
                'icon': 'fa-bullseye',
                'points': 10,
                'condition_type': 'goals_created',
                'condition_value': 1
            },
            {
                'name': 'Người hoàn thành',
                'description': 'Hoàn thành 1 mục tiêu học tập',
                'category': 'goals',
                'level': 'bronze',
                'icon': 'fa-check-circle',
                'points': 20,
                'condition_type': 'goals_completed',
                'condition_value': 1
            },
            {
                'name': 'Người kiên trì',
                'description': 'Hoàn thành 5 mục tiêu học tập',
                'category': 'goals',
                'level': 'silver',
                'icon': 'fa-check-circle',
                'points': 100,
                'condition_type': 'goals_completed',
                'condition_value': 5
            },
            {
                'name': 'Bậc thầy mục tiêu',
                'description': 'Hoàn thành 20 mục tiêu học tập',
                'category': 'goals',
                'level': 'gold',
                'icon': 'fa-check-circle',
                'points': 300,
                'condition_type': 'goals_completed',
                'condition_value': 20
            },
        ]
        
        # Huy hiệu bài kiểm tra
        quiz_badges = [
            {
                'name': 'Người kiểm tra',
                'description': 'Hoàn thành bài kiểm tra đầu tiên',
                'category': 'quizzes',
                'level': 'bronze',
                'icon': 'fa-question-circle',
                'points': 10,
                'condition_type': 'quizzes_completed',
                'condition_value': 1
            },
            {
                'name': 'Người đạt điểm cao',
                'description': 'Đạt điểm tuyệt đối trong 1 bài kiểm tra',
                'category': 'quizzes',
                'level': 'silver',
                'icon': 'fa-star',
                'points': 50,
                'condition_type': 'perfect_quizzes',
                'condition_value': 1
            },
            {
                'name': 'Bậc thầy kiểm tra',
                'description': 'Hoàn thành 20 bài kiểm tra',
                'category': 'quizzes',
                'level': 'gold',
                'icon': 'fa-question-circle',
                'points': 200,
                'condition_type': 'quizzes_completed',
                'condition_value': 20
            },
        ]
        
        # Huy hiệu đặc biệt
        special_badges = [
            {
                'name': 'Người học ban đêm',
                'description': 'Học tập sau 10 giờ tối',
                'category': 'special',
                'level': 'bronze',
                'icon': 'fa-moon',
                'points': 20,
                'condition_type': 'night_study',
                'condition_value': 1
            },
            {
                'name': 'Người học cuối tuần',
                'description': 'Học tập vào cuối tuần',
                'category': 'special',
                'level': 'bronze',
                'icon': 'fa-calendar-week',
                'points': 20,
                'condition_type': 'weekend_study',
                'condition_value': 1
            },
            {
                'name': 'Người học liên tục',
                'description': 'Học tập 7 ngày liên tiếp',
                'category': 'special',
                'level': 'silver',
                'icon': 'fa-calendar-check',
                'points': 100,
                'condition_type': 'streak_days',
                'condition_value': 7
            },
            {
                'name': 'Người học kiên trì',
                'description': 'Học tập 30 ngày liên tiếp',
                'category': 'special',
                'level': 'gold',
                'icon': 'fa-calendar-check',
                'points': 300,
                'condition_type': 'streak_days',
                'condition_value': 30
            },
            {
                'name': 'Người học xuất sắc',
                'description': 'Học tập 100 ngày liên tiếp',
                'category': 'special',
                'level': 'platinum',
                'icon': 'fa-calendar-check',
                'points': 1000,
                'condition_type': 'streak_days',
                'condition_value': 100
            },
        ]
        
        # Gộp tất cả huy hiệu
        all_badges = learning_badges + flashcard_badges + goal_badges + quiz_badges + special_badges
        
        # Tạo huy hiệu
        badges_created = 0
        for badge_data in all_badges:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                badges_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Đã tạo {badges_created} huy hiệu mẫu'))
    
    def create_sample_rewards(self):
        """Tạo các phần thưởng mẫu"""
        rewards = [
            {
                'name': 'Chế độ tối',
                'description': 'Mở khóa chế độ tối cho ứng dụng',
                'points_required': 100,
                'icon': 'fa-moon',
            },
            {
                'name': 'Giao diện tùy chỉnh',
                'description': 'Mở khóa khả năng tùy chỉnh giao diện ứng dụng',
                'points_required': 200,
                'icon': 'fa-palette',
            },
            {
                'name': 'Chủ đề đặc biệt',
                'description': 'Mở khóa chủ đề đặc biệt cho ứng dụng',
                'points_required': 300,
                'icon': 'fa-paint-brush',
            },
            {
                'name': 'Huy hiệu VIP',
                'description': 'Nhận huy hiệu VIP hiển thị trên hồ sơ của bạn',
                'points_required': 500,
                'icon': 'fa-crown',
            },
            {
                'name': 'Tính năng xuất dữ liệu',
                'description': 'Mở khóa khả năng xuất dữ liệu học tập sang các định dạng khác nhau',
                'points_required': 800,
                'icon': 'fa-file-export',
            },
            {
                'name': 'Tính năng phân tích nâng cao',
                'description': 'Mở khóa các biểu đồ và phân tích nâng cao về quá trình học tập',
                'points_required': 1000,
                'icon': 'fa-chart-line',
            },
        ]
        
        # Tạo phần thưởng
        rewards_created = 0
        for reward_data in rewards:
            reward, created = Reward.objects.get_or_create(
                name=reward_data['name'],
                defaults=reward_data
            )
            if created:
                rewards_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Đã tạo {rewards_created} phần thưởng mẫu'))
