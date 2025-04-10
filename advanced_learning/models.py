from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from content.models import Subject, Topic, Lesson

# Import các model mục tiêu học tập và theo dõi thời gian học tập
from .models_learning_goals import LearningGoal, DailyStudyLog

# Hệ thống học tập dựa trên dự án
class Project(models.Model):
    """Dự án học tập thực tế"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='projects')
    difficulty_level = models.IntegerField(choices=[(1, 'Dễ'), (2, 'Trung bình'), (3, 'Khó')], default=1)
    estimated_hours = models.PositiveIntegerField(help_text='Thời gian ước tính để hoàn thành (giờ)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ProjectTask(models.Model):
    """Nhiệm vụ trong dự án"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.project.title} - {self.title}"





# Bài tập thực hành tương tác
class InteractiveExercise(models.Model):
    """Bài tập thực hành tương tác"""
    EXERCISE_TYPES = [
        ('code', 'Bài tập lập trình'),
        ('quiz', 'Câu đố tương tác'),
        ('simulation', 'Mô phỏng'),
        ('game', 'Trò chơi học tập')
    ]

    PROGRAMMING_LANGUAGES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('cpp', 'C++'),
        ('csharp', 'C#'),
        ('php', 'PHP'),
        ('ruby', 'Ruby'),
        ('html_css', 'HTML/CSS')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='interactive_exercises')
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    content = models.TextField(help_text='Nội dung bài tập (có thể là mã HTML, JavaScript, hoặc mã nguồn)')
    solution = models.TextField(help_text='Giải pháp hoặc đáp án', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Các trường mới
    programming_language = models.CharField(max_length=20, choices=PROGRAMMING_LANGUAGES, blank=True, null=True, help_text='Ngôn ngữ lập trình cho bài tập code')
    starter_code = models.TextField(blank=True, null=True, help_text='Mã khởi đầu cho bài tập lập trình')
    test_cases = models.JSONField(default=list, blank=True, null=True, help_text='Các trường hợp kiểm tra cho bài tập lập trình')
    simulation_config = models.JSONField(default=dict, blank=True, null=True, help_text='Cấu hình cho mô phỏng')
    game_config = models.JSONField(default=dict, blank=True, null=True, help_text='Cấu hình cho trò chơi học tập')
    difficulty_level = models.PositiveIntegerField(default=1, help_text='Độ khó của bài tập (1-5)')
    points = models.PositiveIntegerField(default=10, help_text='Điểm thưởng khi hoàn thành bài tập')
    time_limit = models.PositiveIntegerField(blank=True, null=True, help_text='Giới hạn thời gian làm bài (giây)')
    hints = models.JSONField(default=list, blank=True, null=True, help_text='Gợi ý cho bài tập')
    is_public = models.BooleanField(default=True, help_text='Bài tập có công khai không')
    achievements = models.ManyToManyField('Achievement', blank=True, related_name='exercises', help_text='Các thành tích liên quan đến bài tập')

    def __str__(self):
        return self.title

    def get_test_cases_display(self):
        """Hiển thị các trường hợp kiểm tra dưới dạng có thể đọc được"""
        if not self.test_cases:
            return []

        result = []
        for i, test_case in enumerate(self.test_cases):
            display = {
                'id': i + 1,
                'input': test_case.get('input', ''),
                'expected_output': test_case.get('expected_output', ''),
                'is_hidden': test_case.get('is_hidden', False)
            }
            result.append(display)
        return result

    def get_hints_display(self):
        """Hiển thị các gợi ý dưới dạng có thể đọc được"""
        if not self.hints:
            return []

        result = []
        for i, hint in enumerate(self.hints):
            display = {
                'id': i + 1,
                'content': hint.get('content', ''),
                'cost': hint.get('cost', 0)
            }
            result.append(display)
        return result


class ExerciseSubmission(models.Model):
    """Lưu trữ các bài nộp của người dùng"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_submissions')
    exercise = models.ForeignKey(InteractiveExercise, on_delete=models.CASCADE, related_name='submissions')
    submission_content = models.TextField(help_text='Nội dung bài nộp')
    is_correct = models.BooleanField(default=False, help_text='Bài nộp có đúng không')
    feedback = models.TextField(blank=True, null=True, help_text='Phản hồi về bài nộp')
    execution_time = models.FloatField(blank=True, null=True, help_text='Thời gian thực thi (giây)')
    execution_result = models.JSONField(default=dict, blank=True, null=True, help_text='Kết quả thực thi')
    points_earned = models.PositiveIntegerField(default=0, help_text='Điểm được thưởng')
    hints_used = models.JSONField(default=list, blank=True, null=True, help_text='Các gợi ý đã sử dụng')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.exercise.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def calculate_points(self):
        """Tính toán điểm dựa trên độ chính xác và gợi ý đã sử dụng"""
        if not self.is_correct:
            return 0

        # Điểm cơ bản
        points = self.exercise.points

        # Trừ điểm cho mỗi gợi ý đã sử dụng
        if self.hints_used:
            hint_cost = sum(hint.get('cost', 0) for hint in self.hints_used)
            points = max(0, points - hint_cost)

        self.points_earned = points
        self.save(update_fields=['points_earned'])
        return points

# Hệ thống ghi chú Cornell
class CornellNote(models.Model):
    """Ghi chú theo phương pháp Cornell"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cornell_notes')
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='cornell_notes')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='cornell_notes')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='cornell_notes')
    main_notes = models.TextField(help_text='Phần ghi chú chính')
    cue_column = models.TextField(help_text='Phần cột gợi ý (câu hỏi, từ khóa)', blank=True)
    summary = models.TextField(help_text='Phần tóm tắt', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Các trường mới
    is_shared = models.BooleanField(default=False, help_text='Ghi chú có được chia sẻ không')
    share_url = models.CharField(max_length=100, blank=True, null=True, help_text='URL chia sẻ ghi chú')
    next_review_date = models.DateTimeField(null=True, blank=True, help_text='Ngày ôn tập tiếp theo')
    review_count = models.PositiveIntegerField(default=0, help_text='Số lần đã ôn tập')
    last_review_date = models.DateTimeField(null=True, blank=True, help_text='Ngày ôn tập gần nhất')

    def __str__(self):
        return self.title

    def generate_share_url(self):
        """Tạo URL chia sẻ ngẫu nhiên"""
        import uuid
        if not self.share_url:
            self.share_url = str(uuid.uuid4())[:8]
            self.save(update_fields=['share_url'])
        return self.share_url

    def schedule_next_review(self):
        """Lên lịch ôn tập tiếp theo dựa trên Spaced Repetition"""
        from django.utils import timezone
        import math

        # Công thức Spaced Repetition đơn giản
        # Khoảng thời gian tăng dần theo số lần ôn tập
        days = 1
        if self.review_count > 0:
            # 1, 3, 7, 16, 35, 70, ...
            days = math.ceil((2 ** self.review_count) * 0.8)

        self.next_review_date = timezone.now() + timezone.timedelta(days=days)
        self.save(update_fields=['next_review_date'])

    def mark_reviewed(self):
        """Đánh dấu đã ôn tập"""
        from django.utils import timezone

        self.review_count += 1
        self.last_review_date = timezone.now()
        self.schedule_next_review()
        self.save(update_fields=['review_count', 'last_review_date'])

# Phương pháp Feynman Technique
class FeynmanNote(models.Model):
    """Ghi chú theo phương pháp Feynman"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feynman_notes')
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='feynman_notes')
    concept = models.TextField(help_text='Khái niệm cần giải thích')
    explanation = models.TextField(help_text='Giải thích bằng ngôn ngữ đơn giản')
    gaps_identified = models.TextField(help_text='Các lỗ hổng kiến thức đã xác định', blank=True)
    refined_explanation = models.TextField(help_text='Giải thích đã được cải thiện', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Các trường mới
    is_shared = models.BooleanField(default=False, help_text='Ghi chú có được chia sẻ không')
    share_url = models.CharField(max_length=100, blank=True, null=True, help_text='URL chia sẻ ghi chú')
    next_review_date = models.DateTimeField(null=True, blank=True, help_text='Ngày ôn tập tiếp theo')
    review_count = models.PositiveIntegerField(default=0, help_text='Số lần đã ôn tập')
    last_review_date = models.DateTimeField(null=True, blank=True, help_text='Ngày ôn tập gần nhất')

    def __str__(self):
        return self.title

    def generate_share_url(self):
        """Tạo URL chia sẻ ngẫu nhiên"""
        import uuid
        if not self.share_url:
            self.share_url = str(uuid.uuid4())[:8]
            self.save(update_fields=['share_url'])
        return self.share_url

    def schedule_next_review(self):
        """Lên lịch ôn tập tiếp theo dựa trên Spaced Repetition"""
        from django.utils import timezone
        import math

        # Công thức Spaced Repetition đơn giản
        # Khoảng thời gian tăng dần theo số lần ôn tập
        days = 1
        if self.review_count > 0:
            # 1, 3, 7, 16, 35, 70, ...
            days = math.ceil((2 ** self.review_count) * 0.8)

        self.next_review_date = timezone.now() + timezone.timedelta(days=days)
        self.save(update_fields=['next_review_date'])

    def mark_reviewed(self):
        """\u0110ánh dấu đã ôn tập"""
        from django.utils import timezone

        self.review_count += 1
        self.last_review_date = timezone.now()
        self.schedule_next_review()
        self.save(update_fields=['review_count', 'last_review_date'])

# Hệ thống Mind Mapping
class MindMap(models.Model):
    """Sơ đồ tư duy"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mind_maps')
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='mind_maps')
    central_topic = models.CharField(max_length=200, help_text='Chủ đề trung tâm')
    map_data = models.JSONField(help_text='Dữ liệu sơ đồ tư duy dạng JSON')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Các trường mới
    is_shared = models.BooleanField(default=False, help_text='Sơ đồ tư duy có được chia sẻ không')
    share_url = models.CharField(max_length=100, blank=True, null=True, help_text='URL chia sẻ sơ đồ tư duy')
    style_settings = models.JSONField(default=dict, blank=True, null=True, help_text='Các tùy chọn tùy biến (kiểu đường, hình dạng nút, v.v.)')

    def __str__(self):
        return self.title

    def generate_share_url(self):
        """Tạo URL chia sẻ ngẫu nhiên"""
        import uuid
        if not self.share_url:
            self.share_url = str(uuid.uuid4())[:8]
            self.save(update_fields=['share_url'])
        return self.share_url

    def get_default_style_settings(self):
        """Lấy các tùy chọn mặc định"""
        return {
            'theme': 'primary',
            'line_width': 2,
            'line_color': '#555',
            'line_style': 'straight', # straight, curved, bezier
            'node_shape': 'rectangle', # rectangle, rounded, ellipse
            'node_border_width': 1,
            'node_border_color': '#ccc',
            'node_border_radius': 5,
            'node_font_size': 14,
            'node_font_family': 'Arial',
            'node_padding': 10,
            'background_color': '#f8f9fa',
            'background_image': None,
        }

# Pomodoro Timer
class PomodoroSession(models.Model):
    """Phiên học tập Pomodoro"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pomodoro_sessions')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='pomodoro_sessions')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='pomodoro_sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    work_duration = models.PositiveIntegerField(default=25, help_text='Thời gian làm việc (phút)')
    break_duration = models.PositiveIntegerField(default=5, help_text='Thời gian nghỉ (phút)')
    completed_pomodoros = models.PositiveIntegerField(default=0, help_text='Số pomodoro đã hoàn thành')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

# Dự án của người dùng
class UserProject(models.Model):
    """Dự án của người dùng"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_projects')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='user_projects')
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Chưa bắt đầu'),
        ('in_progress', 'Đang thực hiện'),
        ('completed', 'Đã hoàn thành')
    ], default='not_started')
    progress = models.PositiveIntegerField(default=0, help_text='Tiến độ hoàn thành (%)')
    notes = models.TextField(blank=True, null=True, help_text='Ghi chú của người dùng về dự án')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Các trường mới
    is_shared = models.BooleanField(default=False, help_text='Dự án có được chia sẻ không')
    share_url = models.CharField(max_length=100, blank=True, null=True, help_text='URL chia sẻ dự án')
    result_files = models.JSONField(default=dict, blank=True, null=True, help_text='Danh sách các file kết quả dự án')
    rating = models.PositiveIntegerField(default=0, help_text='Đánh giá dự án (0-5 sao)')
    feedback = models.TextField(blank=True, null=True, help_text='Nhận xét về dự án')
    pomodoro_sessions = models.ManyToManyField(PomodoroSession, blank=True, related_name='user_projects', help_text='Các phiên Pomodoro liên quan đến dự án')
    completed_tasks = models.JSONField(default=list, blank=True, null=True, help_text='Danh sách ID các task đã hoàn thành')
    flashcard_sets = models.ManyToManyField('flashcards.FlashcardSet', blank=True, related_name='user_projects', help_text='Các bộ flashcard liên quan đến dự án')
    quizzes = models.ManyToManyField('quizzes.Quiz', blank=True, related_name='user_projects', help_text='Các quiz liên quan đến dự án')

    def __str__(self):
        return f"{self.user.username} - {self.project.title}"

    def generate_share_url(self):
        """Tạo URL chia sẻ ngẫu nhiên"""
        import uuid
        if not self.share_url:
            self.share_url = str(uuid.uuid4())[:8]
            self.save(update_fields=['share_url'])
        return self.share_url

    def add_result_file(self, file_name, file_url, file_type, description=''):
        """Thêm file kết quả vào dự án"""
        if not self.result_files:
            self.result_files = []

        file_info = {
            'id': len(self.result_files) + 1,
            'name': file_name,
            'url': file_url,
            'type': file_type,
            'description': description,
            'uploaded_at': timezone.now().isoformat()
        }

        self.result_files.append(file_info)
        self.save(update_fields=['result_files'])
        return file_info

    def add_flashcard_set(self, flashcard_set):
        """Liên kết bộ flashcard với dự án"""
        self.flashcard_sets.add(flashcard_set)

    def add_quiz(self, quiz):
        """Liên kết quiz với dự án"""
        self.quizzes.add(quiz)

    def add_pomodoro_session(self, pomodoro_session):
        """Liên kết phiên Pomodoro với dự án"""
        self.pomodoro_sessions.add(pomodoro_session)

    def is_task_completed(self, task_id):
        """Kiểm tra xem task có được hoàn thành chưa"""
        if not hasattr(self, 'completed_tasks') or not self.completed_tasks:
            return False
        return str(task_id) in self.completed_tasks

# Bình luận và đánh giá dự án
class ProjectComment(models.Model):
    """Bình luận và đánh giá dự án"""
    user_project = models.ForeignKey(UserProject, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_comments')
    content = models.TextField(help_text='Nội dung bình luận')
    rating = models.PositiveIntegerField(default=0, help_text='Đánh giá (0-5 sao)', validators=[MinValueValidator(0), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bình luận của {self.author.username} về dự án {self.user_project.project.title}"

# Chế độ thi đấu
class CompetitionMode(models.Model):
    """Chế độ thi đấu"""
    DIFFICULTY_LEVELS = [
        (1, 'Dễ'),
        (2, 'Trung bình'),
        (3, 'Khó'),
        (4, 'Rất khó'),
        (5, 'Chuyên gia'),
    ]

    COMPETITION_TYPES = [
        ('individual', 'Cá nhân'),
        ('team', 'Đồng đội'),
        ('live', 'Trực tiếp'),
        ('realtime', 'Thời gian thực'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='competitions')
    lesson = models.ForeignKey('content.Lesson', on_delete=models.SET_NULL, related_name='competitions', null=True, blank=True)
    difficulty_level = models.PositiveSmallIntegerField(choices=DIFFICULTY_LEVELS, default=2)
    competition_type = models.CharField(max_length=20, choices=COMPETITION_TYPES, default='individual')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    time_limit = models.PositiveIntegerField(help_text='Thời gian làm bài (phút)')
    max_participants = models.PositiveIntegerField(default=0, help_text='Số người tham gia tối đa (0 = không giới hạn)')
    is_active = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False, help_text='Đánh dấu cuộc thi nổi bật')
    points = models.PositiveIntegerField(default=100, help_text='Điểm thưởng khi hoàn thành cuộc thi')
    image = models.ImageField(upload_to='competitions/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
            models.Index(fields=['is_active']),
            models.Index(fields=['competition_type']),
        ]

    def __str__(self):
        return self.title

    def get_status(self):
        """Lấy trạng thái hiện tại của cuộc thi"""
        now = timezone.now()
        if self.start_time > now:
            return 'upcoming'
        elif self.end_time < now:
            return 'past'
        elif self.is_active:
            return 'active'
        else:
            return 'inactive'

    def get_participant_count(self):
        """Lấy số người tham gia"""
        return self.participants.count()

    def can_join(self):
        """Kiểm tra xem có thể tham gia cuộc thi không"""
        if not self.is_active:
            return False

        now = timezone.now()
        if now < self.start_time or now > self.end_time:
            return False

        if self.max_participants > 0 and self.get_participant_count() >= self.max_participants:
            return False

        return True

    def get_time_remaining(self):
        """Lấy thời gian còn lại của cuộc thi"""
        now = timezone.now()
        if now > self.end_time:
            return 0

        return (self.end_time - now).total_seconds()

    def update_rankings(self):
        """Cập nhật xếp hạng cho tất cả người tham gia"""
        participants = self.participants.filter(end_time__isnull=False).order_by('-score', 'end_time')

        for i, participant in enumerate(participants):
            participant.rank = i + 1
            participant.save(update_fields=['rank'])

class CompetitionQuestion(models.Model):
    """Câu hỏi trong chế độ thi đấu"""
    QUESTION_TYPES = [
        ('multiple_choice', 'Nhiều lựa chọn'),
        ('single_choice', 'Một lựa chọn'),
        ('true_false', 'Đúng/Sai'),
        ('text', 'Văn bản'),
        ('code', 'Mã lập trình'),
    ]

    competition = models.ForeignKey(CompetitionMode, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='single_choice')
    points = models.PositiveIntegerField(default=1, help_text='Điểm cho câu hỏi này')
    order = models.PositiveIntegerField(default=0)
    time_limit = models.PositiveIntegerField(default=30, help_text='Thời gian trả lời (giây)')
    image = models.ImageField(upload_to='competition_questions/', null=True, blank=True)
    explanation = models.TextField(blank=True, help_text='Giải thích cho đáp án đúng')
    difficulty_level = models.PositiveSmallIntegerField(choices=CompetitionMode.DIFFICULTY_LEVELS, default=2)
    code_template = models.TextField(blank=True, help_text='Mẫu mã cho câu hỏi lập trình')
    test_cases = models.JSONField(default=list, blank=True, help_text='Các trường hợp kiểm tra cho câu hỏi lập trình')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['competition', 'order']),
            models.Index(fields=['question_type']),
        ]

    def __str__(self):
        return f"{self.competition.title} - Câu hỏi {self.order}"

    def get_correct_answers(self):
        """Lấy các đáp án đúng"""
        return self.answers.filter(is_correct=True)

    def get_correct_answer_ids(self):
        """Lấy danh sách ID của các đáp án đúng"""
        return list(self.answers.filter(is_correct=True).values_list('id', flat=True))

    def check_answer(self, answer_ids):
        """Kiểm tra đáp án của người dùng"""
        if not isinstance(answer_ids, list):
            answer_ids = [answer_ids]

        correct_ids = set(self.get_correct_answer_ids())
        user_ids = set(answer_ids)

        if self.question_type == 'multiple_choice':
            # Đối với câu hỏi nhiều lựa chọn, tất cả các đáp án phải đúng
            return correct_ids == user_ids
        else:
            # Đối với câu hỏi một lựa chọn, chỉ cần một đáp án đúng
            return len(correct_ids.intersection(user_ids)) > 0

class CompetitionAnswer(models.Model):
    """Đáp án cho câu hỏi trong chế độ thi đấu"""
    question = models.ForeignKey(CompetitionQuestion, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True, help_text='Giải thích cho đáp án này')
    image = models.ImageField(upload_to='competition_answers/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0, help_text='Thứ tự hiển thị')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['question', 'is_correct']),
        ]

    def __str__(self):
        return f"{self.question} - {self.answer_text[:30]}"

class CompetitionParticipant(models.Model):
    """Người tham gia chế độ thi đấu"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='competition_participations')
    competition = models.ForeignKey(CompetitionMode, on_delete=models.CASCADE, related_name='participants')
    team = models.ForeignKey('CompetitionTeam', on_delete=models.SET_NULL, related_name='members', null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(null=True, blank=True)
    answers = models.JSONField(default=dict, blank=True, help_text='Các câu trả lời của người dùng')
    time_spent = models.PositiveIntegerField(default=0, help_text='Thời gian đã sử dụng (giây)')
    is_shared = models.BooleanField(default=False, help_text='Đã chia sẻ kết quả')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'competition']),
            models.Index(fields=['competition', 'score']),
            models.Index(fields=['competition', 'rank']),
        ]
        unique_together = ['user', 'competition']

    def __str__(self):
        return f"{self.user.username} - {self.competition.title}"

    def calculate_score(self):
        """Tính điểm dựa trên các câu trả lời"""
        if not self.answers:
            return 0

        total_score = 0
        for question_id, answer_data in self.answers.items():
            if answer_data.get('is_correct', False):
                # Lấy câu hỏi tương ứng
                try:
                    question = CompetitionQuestion.objects.get(id=int(question_id))
                    total_score += question.points
                except CompetitionQuestion.DoesNotExist:
                    continue

        return total_score

    def get_correct_answers_count(self):
        """Lấy số câu trả lời đúng"""
        if not self.answers:
            return 0

        return sum(1 for answer in self.answers.values() if answer.get('is_correct', False))

    def get_total_questions_count(self):
        """Lấy tổng số câu hỏi"""
        return self.competition.questions.count()

    def get_accuracy_percentage(self):
        """Lấy tỷ lệ chính xác"""
        total = self.get_total_questions_count()
        if total == 0:
            return 0

        correct = self.get_correct_answers_count()
        return (correct / total) * 100

    def generate_share_image(self):
        """Tạo hình ảnh kết quả để chia sẻ"""
        # TODO: Implement image generation
        pass

# Chế độ thi đấu theo nhóm
class CompetitionTeam(models.Model):
    """Nhóm thi đấu"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='team_logos/', null=True, blank=True)
    competition = models.ForeignKey(CompetitionMode, on_delete=models.CASCADE, related_name='teams')
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams')
    score = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['name', 'competition']
        ordering = ['-score']

    def __str__(self):
        return f"{self.name} - {self.competition.title}"

    def get_members_count(self):
        """Lấy số thành viên trong nhóm"""
        return self.members.count()

    def calculate_team_score(self):
        """Tính điểm của nhóm dựa trên điểm của các thành viên"""
        members = self.members.all()
        if not members:
            return 0

        # Tính tổng điểm của các thành viên
        total_score = sum(member.score for member in members)

        # Cập nhật điểm của nhóm
        self.score = total_score
        self.save(update_fields=['score'])

        return total_score

# Chế độ thi đấu trực tiếp
class LiveCompetition(models.Model):
    """Cuộc thi trực tiếp"""
    STATUS_CHOICES = [
        ('waiting', 'Chờ bắt đầu'),
        ('active', 'Đang diễn ra'),
        ('completed', 'Đã kết thúc'),
        ('cancelled', 'Đã hủy'),
    ]

    competition = models.ForeignKey(CompetitionMode, on_delete=models.CASCADE, related_name='live_sessions')
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_competitions')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    current_question_index = models.PositiveIntegerField(default=0)
    max_participants = models.PositiveIntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Live: {self.title}"

    def get_participants_count(self):
        """Lấy số người tham gia"""
        return self.participants.count()

    def is_full(self):
        """Kiểm tra xem cuộc thi đã đầy chưa"""
        return self.get_participants_count() >= self.max_participants

    def get_current_question(self):
        """Lấy câu hỏi hiện tại"""
        questions = list(self.competition.questions.all().order_by('order'))
        if not questions or self.current_question_index >= len(questions):
            return None
        return questions[self.current_question_index]

    def next_question(self):
        """Chuyển sang câu hỏi tiếp theo"""
        questions_count = self.competition.questions.count()
        if self.current_question_index < questions_count - 1:
            self.current_question_index += 1
            self.save(update_fields=['current_question_index'])
            return True
        return False

class LiveParticipant(models.Model):
    """Người tham gia cuộc thi trực tiếp"""
    live_competition = models.ForeignKey(LiveCompetition, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_participations')
    score = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(null=True, blank=True)
    answers = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['live_competition', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.live_competition.title}"

# Hệ thống đăng ký nhận thông báo
class CompetitionSubscription(models.Model):
    """Người dùng đăng ký nhận thông báo về cuộc thi"""
    NOTIFICATION_TYPES = [
        ('all', 'Tất cả cuộc thi'),
        ('subject', 'Theo chủ đề'),
        ('specific', 'Cuộc thi cụ thể'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='competition_subscriptions')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True, related_name='competition_subscriptions')
    competition = models.ForeignKey(CompetitionMode, on_delete=models.CASCADE, null=True, blank=True, related_name='subscriptions')
    email_notification = models.BooleanField(default=True)
    push_notification = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ('user', 'notification_type', 'subject', 'competition'),
        ]

    def __str__(self):
        if self.notification_type == 'all':
            return f"{self.user.username} - Tất cả cuộc thi"
        elif self.notification_type == 'subject':
            return f"{self.user.username} - {self.subject.name}"
        else:
            return f"{self.user.username} - {self.competition.title}"

# Hệ thống thành tích
class Achievement(models.Model):
    """Thành tích và huy hiệu"""
    ACHIEVEMENT_TYPES = [
        ('exercise', 'Hoàn thành bài tập'),
        ('streak', 'Chuỗi ngày liên tiếp'),
        ('points', 'Điểm số'),
        ('completion', 'Hoàn thành khóa học'),
        ('special', 'Thành tích đặc biệt'),
        ('competition', 'Cuộc thi đấu')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    icon = models.CharField(max_length=100, help_text='Tên biểu tượng Font Awesome')
    points = models.PositiveIntegerField(default=0, help_text='Điểm thưởng khi đạt được thành tích')
    requirement = models.JSONField(default=dict, help_text='Yêu cầu để đạt được thành tích')
    is_hidden = models.BooleanField(default=False, help_text='Thành tích có ẩn không')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# Thành tích của người dùng
class UserAchievement(models.Model):
    """Thành tích đã đạt được của người dùng"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='user_achievements')
    earned_at = models.DateTimeField(auto_now_add=True)
    progress = models.JSONField(default=dict, blank=True, null=True, help_text='Tiến trình đạt được thành tích')

    class Meta:
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f"{self.user.username} - {self.achievement.title}"


# Hệ thống thành tích cuộc thi
class CompetitionAchievement(models.Model):
    """Thành tích liên quan đến cuộc thi"""
    competition = models.ForeignKey(CompetitionMode, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='competitions')
    requirement = models.JSONField(help_text='Yêu cầu để đạt được thành tích')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['competition', 'achievement']

    def __str__(self):
        return f"{self.competition.title} - {self.achievement.title}"

    def check_achievement(self, participant):
        """Kiểm tra xem người tham gia có đạt được thành tích không"""
        req_type = self.requirement.get('type')
        req_value = self.requirement.get('value')

        if req_type == 'min_score':
            return participant.score >= req_value
        elif req_type == 'min_rank':
            return participant.rank is not None and participant.rank <= req_value
        elif req_type == 'accuracy':
            return participant.get_accuracy_percentage() >= req_value
        elif req_type == 'completion_time':
            if not participant.end_time or not participant.start_time:
                return False
            time_taken = (participant.end_time - participant.start_time).total_seconds()
            return time_taken <= req_value

        return False

# Hệ thống thông báo
class Notification(models.Model):
    """Thông báo cho người dùng"""
    NOTIFICATION_TYPES = [
        ('info', 'Thông tin'),
        ('success', 'Thành công'),
        ('warning', 'Cảnh báo'),
        ('danger', 'Quan trọng'),
    ]

    RELATED_FEATURES = [
        ('pomodoro', 'Pomodoro Timer'),
        ('cornell', 'Cornell Notes'),
        ('mindmap', 'Mind Mapping'),
        ('feynman', 'Feynman Technique'),
        ('project', 'Project-Based Learning'),
        ('exercise', 'Interactive Exercises'),
        ('competition', 'Competition Mode'),
        ('system', 'Hệ thống'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advanced_notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    related_feature = models.CharField(max_length=20, choices=RELATED_FEATURES, default='system')
    related_object_id = models.IntegerField(null=True, blank=True)  # ID của đối tượng liên quan (nếu có)
    url = models.CharField(max_length=200, blank=True)  # URL để chuyển hướng khi nhấp vào thông báo
    is_read = models.BooleanField(default=False)  # Đánh dấu đã đọc hay chưa
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

