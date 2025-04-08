from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from content.models import Subject
from advanced_learning.models import Project, ProjectTask

class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho Project-Based Learning'

    def handle(self, *args, **options):
        # Kiểm tra xem đã có dự án nào chưa
        if Project.objects.exists():
            self.stdout.write(self.style.WARNING('Đã có dữ liệu dự án. Bỏ qua việc tạo dữ liệu mẫu.'))
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

        # Tạo dự án 1: Xây dựng ứng dụng Todo List
        todo_app = Project.objects.create(
            title='Xây dựng ứng dụng Todo List',
            description='''
Dự án này sẽ hướng dẫn bạn xây dựng một ứng dụng Todo List đơn giản bằng HTML, CSS và JavaScript.
Bạn sẽ học cách tạo giao diện người dùng, lưu trữ dữ liệu cục bộ và xử lý sự kiện người dùng.

Đây là một dự án tuyệt vời để thực hành các kỹ năng lập trình web cơ bản và hiểu cách các thành phần
khác nhau của một ứng dụng web hoạt động cùng nhau.
            ''',
            subject=programming_subject,
            difficulty_level=1,
            estimated_hours=10
        )
        
        # Tạo các nhiệm vụ cho dự án Todo List
        ProjectTask.objects.create(
            project=todo_app,
            title='Thiết kế giao diện người dùng',
            description='Tạo giao diện người dùng đơn giản với HTML và CSS. Bao gồm một biểu mẫu để thêm công việc mới và một danh sách để hiển thị các công việc.',
            order=1
        )
        
        ProjectTask.objects.create(
            project=todo_app,
            title='Thêm chức năng JavaScript',
            description='Viết mã JavaScript để thêm, xóa và đánh dấu công việc là đã hoàn thành. Sử dụng DOM để tương tác với HTML.',
            order=2
        )
        
        ProjectTask.objects.create(
            project=todo_app,
            title='Lưu trữ dữ liệu cục bộ',
            description='Sử dụng localStorage để lưu trữ danh sách công việc, để dữ liệu không bị mất khi tải lại trang.',
            order=3
        )
        
        ProjectTask.objects.create(
            project=todo_app,
            title='Thêm tính năng lọc và sắp xếp',
            description='Thêm các tùy chọn để lọc công việc (tất cả, hoàn thành, chưa hoàn thành) và sắp xếp theo thứ tự khác nhau.',
            order=4
        )
        
        ProjectTask.objects.create(
            project=todo_app,
            title='Cải thiện giao diện người dùng',
            description='Thêm CSS để làm cho ứng dụng trông đẹp hơn. Thêm hiệu ứng và hoạt ảnh để cải thiện trải nghiệm người dùng.',
            order=5
        )

        # Tạo dự án 2: Xây dựng ứng dụng từ vựng tiếng Anh
        vocab_app = Project.objects.create(
            title='Xây dựng ứng dụng từ vựng tiếng Anh',
            description='''
Dự án này sẽ hướng dẫn bạn xây dựng một ứng dụng học từ vựng tiếng Anh. Ứng dụng sẽ cho phép người dùng
thêm từ mới, ôn tập từ vựng và theo dõi tiến độ học tập.

Bạn sẽ học cách tổ chức dữ liệu, tạo giao diện người dùng thân thiện và triển khai các thuật toán ôn tập
hiệu quả như spaced repetition.
            ''',
            subject=language_subject,
            difficulty_level=2,
            estimated_hours=15
        )
        
        # Tạo các nhiệm vụ cho dự án từ vựng tiếng Anh
        ProjectTask.objects.create(
            project=vocab_app,
            title='Thiết kế cơ sở dữ liệu từ vựng',
            description='Thiết kế cấu trúc dữ liệu để lưu trữ từ vựng, bao gồm từ, nghĩa, ví dụ, phát âm và thông tin ôn tập.',
            order=1
        )
        
        ProjectTask.objects.create(
            project=vocab_app,
            title='Tạo giao diện thêm từ mới',
            description='Xây dựng giao diện cho phép người dùng thêm từ mới vào ứng dụng, bao gồm các trường thông tin cần thiết.',
            order=2
        )
        
        ProjectTask.objects.create(
            project=vocab_app,
            title='Triển khai chức năng ôn tập',
            description='Xây dựng chức năng ôn tập từ vựng với các dạng bài tập khác nhau như chọn nghĩa đúng, điền từ vào chỗ trống.',
            order=3
        )
        
        ProjectTask.objects.create(
            project=vocab_app,
            title='Triển khai thuật toán spaced repetition',
            description='Triển khai thuật toán spaced repetition để lên lịch ôn tập từ vựng một cách hiệu quả dựa trên mức độ nhớ của người dùng.',
            order=4
        )
        
        ProjectTask.objects.create(
            project=vocab_app,
            title='Thêm tính năng theo dõi tiến độ',
            description='Xây dựng trang thống kê để người dùng có thể theo dõi tiến độ học tập, bao gồm số từ đã học, tỷ lệ trả lời đúng và lịch sử ôn tập.',
            order=5
        )

        # Tạo dự án 3: Giải quyết bài toán tối ưu hóa
        optimization = Project.objects.create(
            title='Giải quyết bài toán tối ưu hóa',
            description='''
Dự án này sẽ hướng dẫn bạn giải quyết một bài toán tối ưu hóa thực tế bằng cách sử dụng các thuật toán
tối ưu hóa và lập trình tuyến tính.

Bạn sẽ học cách mô hình hóa vấn đề, triển khai thuật toán và đánh giá hiệu suất của giải pháp. Dự án này
yêu cầu kiến thức về toán học và lập trình.
            ''',
            subject=math_subject,
            difficulty_level=3,
            estimated_hours=20
        )
        
        # Tạo các nhiệm vụ cho dự án tối ưu hóa
        ProjectTask.objects.create(
            project=optimization,
            title='Tìm hiểu về bài toán tối ưu hóa',
            description='Nghiên cứu và tìm hiểu về các loại bài toán tối ưu hóa, bao gồm tối ưu hóa tuyến tính, phi tuyến và tổ hợp.',
            order=1
        )
        
        ProjectTask.objects.create(
            project=optimization,
            title='Mô hình hóa vấn đề',
            description='Chọn một vấn đề thực tế (như lập lịch, định tuyến, phân bổ tài nguyên) và mô hình hóa nó dưới dạng bài toán tối ưu hóa.',
            order=2
        )
        
        ProjectTask.objects.create(
            project=optimization,
            title='Triển khai thuật toán',
            description='Triển khai một thuật toán để giải quyết bài toán tối ưu hóa đã chọn. Có thể sử dụng các thư viện như SciPy, PuLP hoặc OR-Tools.',
            order=3
        )
        
        ProjectTask.objects.create(
            project=optimization,
            title='Đánh giá hiệu suất',
            description='Đánh giá hiệu suất của thuật toán trên các bộ dữ liệu khác nhau. So sánh thời gian chạy, chất lượng giải pháp và khả năng mở rộng.',
            order=4
        )
        
        ProjectTask.objects.create(
            project=optimization,
            title='Cải thiện thuật toán',
            description='Cải thiện thuật toán bằng cách tối ưu hóa mã nguồn, thử nghiệm các phương pháp khác nhau hoặc triển khai các heuristic.',
            order=5
        )

        self.stdout.write(self.style.SUCCESS('Đã tạo thành công dữ liệu mẫu cho Project-Based Learning!'))
