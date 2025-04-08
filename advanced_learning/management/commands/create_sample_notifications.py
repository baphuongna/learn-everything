from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from advanced_learning.models import Notification, CompetitionMode, UserProject

class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho hệ thống thông báo'

    def handle(self, *args, **options):
        # Xóa tất cả thông báo hiện có
        Notification.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Đã xóa tất cả thông báo hiện có.'))

        # Lấy người dùng đầu tiên
        try:
            user = User.objects.first()
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Không tìm thấy người dùng nào. Vui lòng tạo người dùng trước.'))
            return

        # Tạo thông báo chào mừng
        Notification.objects.create(
            user=user,
            title='Chào mừng đến với Học Tập Nâng Cao',
            message='Chào mừng bạn đến với hệ thống Học Tập Nâng Cao! Khám phá các tính năng mới để cải thiện việc học tập của bạn.',
            notification_type='info',
            related_feature='system',
            url=reverse('advanced_learning:dashboard')
        )

        # Tạo thông báo về Pomodoro
        Notification.objects.create(
            user=user,
            title='Bắt đầu với Pomodoro Timer',
            message='Sử dụng Pomodoro Timer để tăng năng suất học tập. Làm việc trong 25 phút, sau đó nghỉ ngơi 5 phút.',
            notification_type='info',
            related_feature='pomodoro',
            url=reverse('advanced_learning:pomodoro_timer')
        )

        # Tạo thông báo về Cornell Notes
        Notification.objects.create(
            user=user,
            title='Cải thiện ghi chú với Cornell Notes',
            message='Phương pháp Cornell Notes giúp bạn tổ chức ghi chú hiệu quả hơn. Hãy thử ngay!',
            notification_type='info',
            related_feature='cornell',
            url=reverse('advanced_learning:cornell_note_list')
        )

        # Tạo thông báo về Mind Mapping
        Notification.objects.create(
            user=user,
            title='Tạo Mind Map đầu tiên của bạn',
            message='Mind Mapping giúp bạn kết nối các ý tưởng và khái niệm một cách trực quan. Tạo Mind Map đầu tiên của bạn ngay hôm nay!',
            notification_type='info',
            related_feature='mindmap',
            url=reverse('advanced_learning:mind_map_list')
        )

        # Tạo thông báo về Feynman Technique
        Notification.objects.create(
            user=user,
            title='Hiểu sâu hơn với Feynman Technique',
            message='Feynman Technique giúp bạn hiểu sâu hơn về một chủ đề bằng cách giải thích nó bằng ngôn ngữ đơn giản.',
            notification_type='info',
            related_feature='feynman',
            url=reverse('advanced_learning:feynman_note_list')
        )

        # Tạo thông báo về Project-Based Learning
        Notification.objects.create(
            user=user,
            title='Học tập thông qua dự án',
            message='Học tập dựa trên dự án giúp bạn áp dụng kiến thức vào thực tiễn. Khám phá các dự án có sẵn hoặc tạo dự án của riêng bạn!',
            notification_type='info',
            related_feature='project',
            url=reverse('advanced_learning:project_list')
        )

        # Tạo thông báo về Interactive Exercises
        Notification.objects.create(
            user=user,
            title='Thực hành với bài tập tương tác',
            message='Bài tập tương tác giúp bạn củng cố kiến thức thông qua thực hành. Hãy thử ngay!',
            notification_type='info',
            related_feature='exercise',
            url=reverse('advanced_learning:dashboard')
        )

        # Tạo thông báo về Competition Mode
        Notification.objects.create(
            user=user,
            title='Tham gia cuộc thi để kiểm tra kiến thức',
            message='Tham gia các cuộc thi để kiểm tra kiến thức và so sánh với những người học khác. Xem danh sách cuộc thi ngay!',
            notification_type='info',
            related_feature='competition',
            url=reverse('advanced_learning:competition_list')
        )

        # Tạo thông báo về cuộc thi sắp diễn ra
        try:
            competition = CompetitionMode.objects.filter(is_active=True).first()
            if competition:
                Notification.objects.create(
                    user=user,
                    title=f'Cuộc thi sắp diễn ra: {competition.title}',
                    message=f'Cuộc thi {competition.title} sẽ bắt đầu vào {competition.start_time.strftime("%d/%m/%Y %H:%M")}. Hãy chuẩn bị sẵn sàng!',
                    notification_type='info',
                    related_feature='competition',
                    related_object_id=competition.id,
                    url=reverse('advanced_learning:competition_detail', args=[competition.id])
                )
        except:
            pass

        # Tạo thông báo về dự án cần cập nhật
        try:
            project = UserProject.objects.filter(user=user, status='in_progress').first()
            if project:
                Notification.objects.create(
                    user=user,
                    title=f'Nhắc nhở cập nhật dự án: {project.project.title}',
                    message=f'Dự án {project.project.title} của bạn cần được cập nhật. Hãy cập nhật tiến độ để duy trì đà học tập!',
                    notification_type='warning',
                    related_feature='project',
                    related_object_id=project.id,
                    url=reverse('advanced_learning:project_detail', args=[project.project.id])
                )
        except:
            pass

        self.stdout.write(self.style.SUCCESS('Đã tạo thành công dữ liệu mẫu cho hệ thống thông báo!'))
