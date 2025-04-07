from django.core.management.base import BaseCommand
from content.models import Subject, Lesson
from accounts.models import UserProfile
from flashcards.models import Flashcard
from utils.image_utils import ensure_subject_image, ensure_profile_image, ensure_lesson_image, ensure_flashcard_image

class Command(BaseCommand):
    help = 'Tạo ảnh mặc định cho các đối tượng không có ảnh'

    def handle(self, *args, **options):
        # Tạo ảnh cho các chủ đề
        subjects_without_image = Subject.objects.filter(icon='')
        self.stdout.write(f'Tìm thấy {subjects_without_image.count()} chủ đề không có ảnh')

        for subject in subjects_without_image:
            ensure_subject_image(subject)
            self.stdout.write(f'Đã tạo ảnh cho chủ đề: {subject.name}')

        # Tạo ảnh cho các hồ sơ người dùng
        profiles_without_image = UserProfile.objects.filter(avatar='')
        self.stdout.write(f'Tìm thấy {profiles_without_image.count()} hồ sơ không có ảnh')

        for profile in profiles_without_image:
            ensure_profile_image(profile)
            self.stdout.write(f'Đã tạo ảnh cho hồ sơ: {profile.user.username}')

        # Tạo ảnh cho các bài học
        lessons_without_image = Lesson.objects.filter(image='')
        self.stdout.write(f'Tìm thấy {lessons_without_image.count()} bài học không có ảnh')

        for lesson in lessons_without_image:
            ensure_lesson_image(lesson)
            self.stdout.write(f'Đã tạo ảnh cho bài học: {lesson.title}')

        # Tạo ảnh cho các flashcard
        flashcards_without_image = Flashcard.objects.filter(image='')
        self.stdout.write(f'Tìm thấy {flashcards_without_image.count()} flashcard không có ảnh')

        for flashcard in flashcards_without_image:
            ensure_flashcard_image(flashcard)
            self.stdout.write(f'Đã tạo ảnh cho flashcard: {flashcard.front[:30]}...')

        self.stdout.write(self.style.SUCCESS('Hoàn thành việc tạo ảnh mặc định!'))
