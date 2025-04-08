from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from content.models import Subject
from advanced_learning.models import CompetitionMode, CompetitionQuestion, CompetitionAnswer

class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho Competition Mode'

    def handle(self, *args, **options):
        # Kiểm tra xem đã có cuộc thi nào chưa
        if CompetitionMode.objects.exists():
            self.stdout.write(self.style.WARNING('Đã có dữ liệu cuộc thi. Bỏ qua việc tạo dữ liệu mẫu.'))
            return

        # Lấy hoặc tạo chủ đề
        programming_subject, created = Subject.objects.get_or_create(
            name='Lập trình',
            defaults={'description': 'Học lập trình và phát triển phần mềm'}
        )
        
        language_subject, created = Subject.objects.get_or_create(
            name='Ngoại ngữ',
            defaults={'description': 'Học ngoại ngữ và giao tiếp'}
        )
        
        math_subject, created = Subject.objects.get_or_create(
            name='Toán học',
            defaults={'description': 'Học toán học và ứng dụng'}
        )

        # Tạo cuộc thi 1: Kiến thức lập trình Python cơ bản
        now = timezone.now()
        python_quiz = CompetitionMode.objects.create(
            title='Kiến thức lập trình Python cơ bản',
            description='''
Kiểm tra kiến thức cơ bản về ngôn ngữ lập trình Python. Cuộc thi này bao gồm các câu hỏi về cú pháp,
cấu trúc dữ liệu, hàm, lớp và các khái niệm cơ bản khác trong Python.

Đây là một cuộc thi tuyệt vời để kiểm tra kiến thức của bạn về Python và so sánh với những người học khác.
            ''',
            subject=programming_subject,
            start_time=now,
            end_time=now + timezone.timedelta(days=7),
            time_limit=15,
            max_participants=0,
            is_active=True
        )
        
        # Tạo câu hỏi cho cuộc thi Python
        question1 = CompetitionQuestion.objects.create(
            competition=python_quiz,
            question_text='Đâu là cách khai báo một list rỗng trong Python?',
            points=1,
            order=0
        )
        
        CompetitionAnswer.objects.create(
            question=question1,
            answer_text='list = []',
            is_correct=True
        )
        
        CompetitionAnswer.objects.create(
            question=question1,
            answer_text='list = {}',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question1,
            answer_text='list = ()',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question1,
            answer_text='list = new List()',
            is_correct=False
        )
        
        question2 = CompetitionQuestion.objects.create(
            competition=python_quiz,
            question_text='Đâu là cách đúng để mở một file để đọc trong Python?',
            points=1,
            order=1
        )
        
        CompetitionAnswer.objects.create(
            question=question2,
            answer_text='file = open("file.txt", "r")',
            is_correct=True
        )
        
        CompetitionAnswer.objects.create(
            question=question2,
            answer_text='file = open("file.txt", "w")',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question2,
            answer_text='file = read("file.txt")',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question2,
            answer_text='file = File.open("file.txt")',
            is_correct=False
        )
        
        question3 = CompetitionQuestion.objects.create(
            competition=python_quiz,
            question_text='Đâu là kết quả của biểu thức sau: 3 * 2 ** 2?',
            points=2,
            order=2
        )
        
        CompetitionAnswer.objects.create(
            question=question3,
            answer_text='12',
            is_correct=True
        )
        
        CompetitionAnswer.objects.create(
            question=question3,
            answer_text='36',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question3,
            answer_text='9',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question3,
            answer_text='6',
            is_correct=False
        )
        
        question4 = CompetitionQuestion.objects.create(
            competition=python_quiz,
            question_text='Đâu là cách đúng để định nghĩa một hàm trong Python?',
            points=1,
            order=3
        )
        
        CompetitionAnswer.objects.create(
            question=question4,
            answer_text='def my_function():',
            is_correct=True
        )
        
        CompetitionAnswer.objects.create(
            question=question4,
            answer_text='function my_function():',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question4,
            answer_text='def = my_function():',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question4,
            answer_text='func my_function():',
            is_correct=False
        )
        
        question5 = CompetitionQuestion.objects.create(
            competition=python_quiz,
            question_text='Đâu là cách đúng để tạo một class trong Python?',
            points=2,
            order=4
        )
        
        CompetitionAnswer.objects.create(
            question=question5,
            answer_text='class MyClass:',
            is_correct=True
        )
        
        CompetitionAnswer.objects.create(
            question=question5,
            answer_text='class = MyClass:',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question5,
            answer_text='def MyClass:',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question5,
            answer_text='create MyClass:',
            is_correct=False
        )

        # Tạo cuộc thi 2: Từ vựng tiếng Anh cơ bản
        english_quiz = CompetitionMode.objects.create(
            title='Từ vựng tiếng Anh cơ bản',
            description='''
Kiểm tra kiến thức từ vựng tiếng Anh cơ bản. Cuộc thi này bao gồm các câu hỏi về nghĩa của từ,
từ đồng nghĩa, từ trái nghĩa và cách sử dụng từ trong câu.

Đây là một cuộc thi tuyệt vời để kiểm tra vốn từ vựng tiếng Anh của bạn và so sánh với những người học khác.
            ''',
            subject=language_subject,
            start_time=now + timezone.timedelta(days=1),
            end_time=now + timezone.timedelta(days=8),
            time_limit=10,
            max_participants=0,
            is_active=True
        )
        
        # Tạo câu hỏi cho cuộc thi tiếng Anh
        question1 = CompetitionQuestion.objects.create(
            competition=english_quiz,
            question_text='Đâu là từ đồng nghĩa với "happy"?',
            points=1,
            order=0
        )
        
        CompetitionAnswer.objects.create(
            question=question1,
            answer_text='joyful',
            is_correct=True
        )
        
        CompetitionAnswer.objects.create(
            question=question1,
            answer_text='sad',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question1,
            answer_text='angry',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question1,
            answer_text='tired',
            is_correct=False
        )
        
        question2 = CompetitionQuestion.objects.create(
            competition=english_quiz,
            question_text='Đâu là từ trái nghĩa với "big"?',
            points=1,
            order=1
        )
        
        CompetitionAnswer.objects.create(
            question=question2,
            answer_text='small',
            is_correct=True
        )
        
        CompetitionAnswer.objects.create(
            question=question2,
            answer_text='large',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question2,
            answer_text='huge',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question2,
            answer_text='tall',
            is_correct=False
        )
        
        question3 = CompetitionQuestion.objects.create(
            competition=english_quiz,
            question_text='Đâu là nghĩa của từ "apple" trong tiếng Việt?',
            points=1,
            order=2
        )
        
        CompetitionAnswer.objects.create(
            question=question3,
            answer_text='Quả táo',
            is_correct=True
        )
        
        CompetitionAnswer.objects.create(
            question=question3,
            answer_text='Quả cam',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question3,
            answer_text='Quả chuối',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question3,
            answer_text='Quả dứa',
            is_correct=False
        )
        
        question4 = CompetitionQuestion.objects.create(
            competition=english_quiz,
            question_text='Đâu là cách đúng để hỏi tên ai đó trong tiếng Anh?',
            points=2,
            order=3
        )
        
        CompetitionAnswer.objects.create(
            question=question4,
            answer_text='What is your name?',
            is_correct=True
        )
        
        CompetitionAnswer.objects.create(
            question=question4,
            answer_text='How is your name?',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question4,
            answer_text='Who is your name?',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question4,
            answer_text='Where is your name?',
            is_correct=False
        )
        
        question5 = CompetitionQuestion.objects.create(
            competition=english_quiz,
            question_text='Đâu là cách đúng để nói "Tôi yêu bạn" trong tiếng Anh?',
            points=1,
            order=4
        )
        
        CompetitionAnswer.objects.create(
            question=question5,
            answer_text='I love you',
            is_correct=True
        )
        
        CompetitionAnswer.objects.create(
            question=question5,
            answer_text='I am love you',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question5,
            answer_text='I loving you',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question5,
            answer_text='Me love you',
            is_correct=False
        )

        # Tạo cuộc thi 3: Toán học cơ bản
        math_quiz = CompetitionMode.objects.create(
            title='Toán học cơ bản',
            description='''
Kiểm tra kiến thức toán học cơ bản. Cuộc thi này bao gồm các câu hỏi về phép tính cơ bản,
hình học, đại số và các khái niệm toán học cơ bản khác.

Đây là một cuộc thi tuyệt vời để kiểm tra kiến thức toán học của bạn và so sánh với những người học khác.
            ''',
            subject=math_subject,
            start_time=now - timezone.timedelta(days=1),
            end_time=now + timezone.timedelta(days=6),
            time_limit=20,
            max_participants=0,
            is_active=True
        )
        
        # Tạo câu hỏi cho cuộc thi toán học
        question1 = CompetitionQuestion.objects.create(
            competition=math_quiz,
            question_text='Bao nhiêu là 2 + 2?',
            points=1,
            order=0
        )
        
        CompetitionAnswer.objects.create(
            question=question1,
            answer_text='4',
            is_correct=True
        )
        
        CompetitionAnswer.objects.create(
            question=question1,
            answer_text='3',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question1,
            answer_text='5',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question1,
            answer_text='2',
            is_correct=False
        )
        
        question2 = CompetitionQuestion.objects.create(
            competition=math_quiz,
            question_text='Bao nhiêu là 5 * 5?',
            points=1,
            order=1
        )
        
        CompetitionAnswer.objects.create(
            question=question2,
            answer_text='25',
            is_correct=True
        )
        
        CompetitionAnswer.objects.create(
            question=question2,
            answer_text='10',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question2,
            answer_text='20',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question2,
            answer_text='30',
            is_correct=False
        )
        
        question3 = CompetitionQuestion.objects.create(
            competition=math_quiz,
            question_text='Bao nhiêu là căn bậc hai của 16?',
            points=2,
            order=2
        )
        
        CompetitionAnswer.objects.create(
            question=question3,
            answer_text='4',
            is_correct=True
        )
        
        CompetitionAnswer.objects.create(
            question=question3,
            answer_text='2',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question3,
            answer_text='8',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question3,
            answer_text='6',
            is_correct=False
        )
        
        question4 = CompetitionQuestion.objects.create(
            competition=math_quiz,
            question_text='Đâu là công thức tính diện tích hình tròn?',
            points=2,
            order=3
        )
        
        CompetitionAnswer.objects.create(
            question=question4,
            answer_text='πr²',
            is_correct=True
        )
        
        CompetitionAnswer.objects.create(
            question=question4,
            answer_text='2πr',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question4,
            answer_text='πd',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question4,
            answer_text='r²',
            is_correct=False
        )
        
        question5 = CompetitionQuestion.objects.create(
            competition=math_quiz,
            question_text='Bao nhiêu là 10% của 50?',
            points=1,
            order=4
        )
        
        CompetitionAnswer.objects.create(
            question=question5,
            answer_text='5',
            is_correct=True
        )
        
        CompetitionAnswer.objects.create(
            question=question5,
            answer_text='10',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question5,
            answer_text='0.5',
            is_correct=False
        )
        
        CompetitionAnswer.objects.create(
            question=question5,
            answer_text='50',
            is_correct=False
        )

        self.stdout.write(self.style.SUCCESS('Đã tạo thành công dữ liệu mẫu cho Competition Mode!'))
