# Memory Bank - Nền Tảng Học Tập

## 1. Tổng quan dự án

### 1.1. Mục đích và mục tiêu

Nền Tảng Học Tập là một ứng dụng web được xây dựng bằng Django, nhằm giúp người dùng học tập hiệu quả với các phương pháp khoa học như Active Recall, Spaced Repetition, Kumon, Kaizen, và Zanshin. Dự án hướng đến việc tạo ra một nền tảng học tập toàn diện, hỗ trợ nhiều chủ đề học tập khác nhau từ ngôn ngữ đến lập trình và toán học.

### 1.2. Phạm vi dự án

- Hỗ trợ đa dạng chủ đề học tập: Tiếng Anh, Tiếng Trung, Python, Java, Toán học, v.v.
- Cung cấp nhiều phương pháp học tập hiệu quả
- Theo dõi tiến độ học tập của người dùng
- Quản lý hồ sơ người dùng và mục tiêu học tập
- Lưu trữ và quản lý ghi nhớ cá nhân

## 2. Kiến trúc hệ thống

### 2.1. Mô hình MVC/MTV

Dự án sử dụng mô hình MTV (Model-Template-View) của Django:
- **Model**: Định nghĩa cấu trúc dữ liệu và logic nghiệp vụ
- **Template**: Hiển thị giao diện người dùng
- **View**: Xử lý yêu cầu từ người dùng và trả về phản hồi

### 2.2. Cấu trúc dự án

```
learning_platform/
├── accounts/            # Quản lý người dùng, hồ sơ và tiến độ học tập
├── content/             # Quản lý chủ đề, bài học và nội dung học tập
├── flashcards/          # Hệ thống flashcard và Spaced Repetition
├── quizzes/             # Hệ thống bài kiểm tra và đánh giá
├── memory_bank/         # Ngân hàng ghi nhớ
├── learning_platform/   # Cấu hình chính của dự án
├── static/              # Tài nguyên tĩnh (CSS, JS, hình ảnh)
├── templates/           # Templates HTML
├── media/               # Tập tin người dùng tải lên
├── manage.py            # Script quản lý Django
└── requirements.txt     # Danh sách các thư viện cần thiết
```

### 2.3. Luồng dữ liệu

1. Người dùng gửi yêu cầu đến server
2. URL dispatcher chuyển yêu cầu đến view tương ứng
3. View tương tác với model để lấy/cập nhật dữ liệu
4. View trả về template với dữ liệu đã xử lý
5. Template được render và trả về cho người dùng

## 3. Các ứng dụng và tính năng

### 3.1. Accounts

**Mô hình dữ liệu:**
- `UserProfile`: Thông tin bổ sung của người dùng
- `UserProgress`: Theo dõi tiến độ học tập
- `StudySession`: Ghi lại các phiên học tập
- `Badge`: Huy hiệu thành tích
- `UserBadge`: Huy hiệu của người dùng
- `RewardPoint`: Điểm thưởng của người dùng
- `Reward`: Phần thưởng có thể đổi
- `UserReward`: Phần thưởng đã đổi của người dùng

**Tính năng chính:**
- Đăng ký, đăng nhập, đăng xuất
- Quản lý hồ sơ người dùng
- Theo dõi tiến độ học tập
- Ghi lại thời gian học tập
- Đặt mục tiêu học tập
- Hệ thống thành tích và huy hiệu
- Hệ thống điểm thưởng và phần thưởng
- Theo dõi chuỗi ngày liên tiếp hoàn thành mục tiêu

### 3.2. Content

**Mô hình dữ liệu:**
- `Subject`: Chủ đề học tập (Tiếng Anh, Python, v.v.)
- `Topic`: Chủ đề con trong mỗi Subject
- `Lesson`: Bài học cụ thể trong mỗi Topic

**Tính năng chính:**
- Duyệt qua các chủ đề học tập
- Xem nội dung bài học
- Đánh dấu bài học đã hoàn thành
- Yêu thích chủ đề

### 3.3. Flashcards

**Mô hình dữ liệu:**
- `FlashcardSet`: Tập hợp flashcard, liên kết với Lesson
- `Flashcard`: Card cá nhân, có mặt trước và mặt sau
- `SpacedRepetitionSchedule`: Lịch ôn tập theo phương pháp Spaced Repetition

**Tính năng chính:**
- Tạo và quản lý bộ flashcard
- Học tập với flashcard
- Ôn tập theo lịch Spaced Repetition
- Đánh giá mức độ nhớ

### 3.4. Quizzes

**Mô hình dữ liệu:**
- `Quiz`: Bộ câu hỏi trắc nghiệm, liên kết với Lesson
- `Question`: Câu hỏi trong quiz
- `Answer`: Các đáp án cho câu hỏi
- `QuizAttempt`: Lưu lại các lần làm quiz
- `UserAnswer`: Lưu lại câu trả lời của người dùng

**Tính năng chính:**
- Làm bài kiểm tra
- Tính điểm tự động
- Xem kết quả và giải thích
- Theo dõi lịch sử làm bài

### 3.5. Memory Bank

**Mô hình dữ liệu:**
- `MemoryCategory`: Danh mục phân loại các ghi nhớ
- `MemoryItem`: Các ghi nhớ của người dùng
- `MemoryAttachment`: Tập tin đính kèm cho ghi nhớ

**Tính năng chính:**
- Quản lý danh mục ghi nhớ
- Tạo, chỉnh sửa, xóa ghi nhớ
- Đính kèm tập tin
- Tìm kiếm và lọc ghi nhớ
- Ôn tập ghi nhớ theo phương pháp Spaced Repetition
- Đánh dấu ghi nhớ yêu thích

### 3.6. Learning Goals

**Mô hình dữ liệu:**
- `LearningGoal`: Mục tiêu học tập của người dùng
- `GoalProgress`: Tiến độ đạt mục tiêu
- `GoalCollaborator`: Người cộng tác trong mục tiêu
- `GoalComment`: Bình luận về mục tiêu
- `GoalInvitation`: Lời mời tham gia mục tiêu

**Tính năng chính:**
- Tạo và quản lý mục tiêu học tập
- Theo dõi tiến độ đạt mục tiêu
- Nhắc nhở khi chưa đạt mục tiêu
- Báo cáo tiến độ định kỳ
- Biểu đồ tiến độ theo thời gian
- Thống kê mục tiêu theo danh mục
- Chia sẻ mục tiêu với bạn bè hoặc nhóm học tập
- Cộng tác trong mục tiêu học tập
- Bình luận và thảo luận về mục tiêu
- Xuất mục tiêu sang định dạng iCalendar
- Tích hợp với Google Calendar
- Phần thưởng khi hoàn thành mục tiêu

## 4. Công nghệ và thư viện

### 4.1. Backend

- **Django 5.2**: Framework web Python
- **Supabase (PostgreSQL)**: Cơ sở dữ liệu chính
- **SQLite**: Cơ sở dữ liệu dự phòng cho môi trường phát triển

### 4.2. Frontend

- **Bootstrap 5**: Framework CSS
- **jQuery**: Thư viện JavaScript
- **Font Awesome**: Thư viện icon
- **Chart.js**: Thư viện vẽ biểu đồ
- **Moment.js**: Thư viện xử lý thời gian

### 4.3. Thư viện Python

- **Pillow**: Xử lý hình ảnh
- **django-crispy-forms**: Tạo form đẹp
- **crispy-bootstrap4**: Template pack cho crispy-forms
- **django-summernote**: Trình soạn thảo văn bản phong phú
- **markdown**: Xử lý Markdown
- **supabase-py**: Thư viện Python cho Supabase
- **psycopg2-binary**: Kết nối PostgreSQL
- **python-dotenv**: Đọc biến môi trường từ file .env
- **dj-database-url**: Xử lý URL kết nối cơ sở dữ liệu
- **icalendar**: Tạo và xử lý file iCalendar (.ics)
- **requests**: Gọi API và tương tác với web
- **django-csp**: Chính sách bảo mật nội dung
- **bleach**: Làm sạch và xử lý HTML an toàn

## 5. Hướng dẫn cài đặt

### 5.1. Yêu cầu hệ thống

- Python 3.8+
- pip (trình quản lý gói Python)
- Virtualenv (tùy chọn, nhưng được khuyến nghị)
- Tài khoản Supabase (cho cơ sở dữ liệu PostgreSQL)

### 5.2. Các bước cài đặt

1. **Clone repository:**
   ```
   git clone https://github.com/yourusername/learning-platform.git
   cd learning-platform
   ```

2. **Tạo môi trường ảo và kích hoạt:**
   ```
   python -m venv venv
   source venv/bin/activate  # Trên Linux/Mac
   venv\Scripts\activate     # Trên Windows
   ```

3. **Cài đặt các thư viện cần thiết:**
   ```
   pip install -r requirements.txt
   ```

4. **Cài đặt Git hooks để bảo vệ thông tin nhạy cảm:**
   - Trên Windows:
     ```
     scripts\install_hooks.bat
     ```
   - Trên Linux/Mac:
     ```
     bash scripts/install_hooks.sh
     ```

5. **Cấu hình kết nối Supabase:**
   - Sử dụng script tự động để tạo file `.env`:
     ```
     python scripts/setup_env.py
     ```
   - Hoặc sao chép file `.env.example` thành `.env` và cập nhật thủ công
   - Xem hướng dẫn chi tiết tại `docs/supabase_integration.md`
   - **Lưu ý**: Không bao giờ commit file `.env` lên Git (Git hooks sẽ ngăn chặn điều này)

6. **Tạo cơ sở dữ liệu:**
   ```
   python manage.py migrate
   ```

7. **Tạo tài khoản admin:**
   ```
   python manage.py createsuperuser
   ```

8. **Tạo dữ liệu mẫu (tùy chọn):**
   ```
   python sample_data.py
   ```

9. **Chạy máy chủ phát triển:**
   ```
   python manage.py runserver
   ```

10. **Truy cập ứng dụng tại http://127.0.0.1:8000/**

## 6. Hướng dẫn sử dụng

### 6.1. Quản lý chủ đề và bài học

1. **Duyệt chủ đề:**
   - Truy cập "Chủ Đề" từ menu chính
   - Xem danh sách các chủ đề học tập

2. **Xem bài học:**
   - Chọn một chủ đề
   - Chọn một chủ đề con
   - Chọn một bài học để xem nội dung

3. **Đánh dấu bài học hoàn thành:**
   - Khi xem bài học, nhấn nút "Đánh dấu hoàn thành"

### 6.2. Sử dụng Flashcards

1. **Xem danh sách flashcard:**
   - Truy cập "Flashcards" từ menu chính
   - Chọn một bộ flashcard để học

2. **Học với flashcard:**
   - Nhấp vào flashcard để lật
   - Đánh giá mức độ nhớ (Khó nhớ, Nhớ mờ mờ, Nhớ rõ)

3. **Xem flashcards cần ôn tập:**
   - Truy cập "Flashcards cần ôn tập" để xem các flashcard đến hạn ôn tập

### 6.3. Làm bài kiểm tra

1. **Xem danh sách bài kiểm tra:**
   - Truy cập "Quizzes" từ menu chính
   - Chọn một bài kiểm tra để làm

2. **Làm bài kiểm tra:**
   - Nhấn "Bắt Đầu Làm Bài"
   - Trả lời các câu hỏi
   - Nhấn "Nộp Bài" khi hoàn thành

3. **Xem kết quả:**
   - Xem điểm số và đánh giá
   - Xem giải thích cho các câu trả lời

### 6.4. Sử dụng Memory Bank

1. **Quản lý danh mục:**
   - Truy cập "Memory Bank" từ menu chính
   - Chọn "Quản Lý Danh Mục"
   - Tạo, chỉnh sửa hoặc xóa danh mục

2. **Quản lý ghi nhớ:**
   - Tạo ghi nhớ mới từ trang chủ Memory Bank hoặc từ danh mục
   - Chỉnh sửa hoặc xóa ghi nhớ từ trang chi tiết
   - Đánh dấu ghi nhớ yêu thích

3. **Ôn tập ghi nhớ:**
   - Xem ghi nhớ cần ôn tập từ trang chủ Memory Bank
   - Đánh giá mức độ nhớ để lên lịch ôn tập tiếp theo

4. **Tìm kiếm ghi nhớ:**
   - Sử dụng chức năng tìm kiếm từ trang chủ Memory Bank
   - Lọc theo danh mục, mức độ ưu tiên, hoặc trạng thái yêu thích

## 7. Vấn đề đã gặp và giải pháp

### 7.1. Vấn đề với crispy-forms

**Vấn đề:** Lỗi "TemplateDoesNotExist at /accounts/login/ bootstrap4/uni_form.html" khi truy cập trang đăng nhập.

**Giải pháp:** Thêm 'crispy_bootstrap4' vào INSTALLED_APPS và cài đặt phiên bản phù hợp.

**Trạng thái:** Đã sửa xong

### 7.2. Vấn đề với django-summernote

**Vấn đề:** Trình soạn thảo Summernote không hiển thị đúng trong form tạo/chỉnh sửa ghi nhớ.

**Giải pháp:** Thêm 'django_summernote' vào INSTALLED_APPS, cấu hình SUMMERNOTE_CONFIG và sử dụng SummernoteWidget.

**Trạng thái:** Đã sửa xong

### 7.3. Vấn đề với pre-commit hook

**Vấn đề:** Script pre-commit hook gặp lỗi mã hóa ký tự Unicode trên Windows, gây ra lỗi 'charmap' codec can't encode character.

**Giải pháp:** Sử dụng ký tự ASCII thuần túy trong script thay vì Unicode, bỏ qua thư mục .venv và các thư viện bên thứ ba.

**Trạng thái:** Đã sửa xong

### 7.4. Vấn đề với thông tin nhạy cảm trong mã nguồn

**Vấn đề:** Script kiểm tra thông tin nhạy cảm phát hiện nhiều báo cáo giả dương, đặc biệt là với các chứng chỉ SSL.

**Giải pháp:** Cải thiện script để bỏ qua các chứng chỉ SSL và các mẫu an toàn khác, giảm báo cáo giả dương.

**Trạng thái:** Đã sửa xong

## 8. Kế hoạch phát triển tương lai

### 8.1. Tính năng mới

#### 8.1.1. Tính năng học tập nâng cao
- **Hệ thống học tập dựa trên dự án**: Tạo các dự án thực tế cho người học áp dụng kiến thức
- **Bài tập thực hành tương tác**: Môi trường thực hành code trực tiếp cho lập trình
- **Hệ thống ghi chú Cornell**: Tích hợp phương pháp ghi chú có cấu trúc
- **Phương pháp Feynman Technique**: Công cụ giải thích khái niệm phức tạp bằng ngôn ngữ đơn giản
- **Hệ thống Mind Mapping**: Công cụ tạo sơ đồ tư duy trực quan
- **Pomodoro Timer tích hợp**: Hẹn giờ học tập theo phương pháp Pomodoro
- **Chế độ thi đấu**: Học tập dưới áp lực thời gian để tăng khả năng tập trung

#### 8.1.2. Tính năng xã hội và cộng đồng
- **Diễn đàn thảo luận**: Diễn đàn riêng cho từng chủ đề học tập
- **Nhóm học tập**: Tạo và tham gia nhóm học tập
- **Chia sẻ bộ flashcard và ghi nhớ**: Chia sẻ tài nguyên học tập với người dùng khác
- **Hệ thống mentor/mentee**: Kết nối người học với người hướng dẫn
- **Học tập cộng tác**: Làm việc cùng nhau trên một dự án hoặc bài tập
- **Thách thức học tập**: Tạo và tham gia các thách thức học tập
- **Bảng xếp hạng và huy hiệu**: Tạo động lực học tập thông qua gamification
- **Chia sẻ mục tiêu học tập**: Cho phép chia sẻ mục tiêu với bạn bè hoặc nhóm học tập
- **Cộng tác mục tiêu**: Cho phép nhiều người cùng cập nhật tiến độ một mục tiêu
- **Bình luận và thảo luận mục tiêu**: Trao đổi về mục tiêu học tập

#### 8.1.3. Tính năng cá nhân hóa
- **Lộ trình học tập cá nhân hóa**: Tạo lộ trình dựa trên mục tiêu và trình độ
- **Hệ thống đề xuất nội dung**: Đề xuất bài học dựa trên sở thích và tiến độ
- **Điều chỉnh độ khó tự động**: Tự động điều chỉnh độ khó dựa trên khả năng người dùng
- **Tùy chỉnh giao diện**: Chọn chủ đề và màu sắc theo sở thích
- **Nhắc nhở học tập cá nhân hóa**: Nhắc nhở dựa trên thời gian học tập tối ưu
- **Mục tiêu học tập chi tiết**: Thiết lập và theo dõi mục tiêu ngắn, trung và dài hạn
- **Phân tích điểm mạnh, điểm yếu**: Xác định chủ đề mạnh và yếu dựa trên kết quả

#### 8.1.4. Tích hợp công nghệ mới
- **Trợ lý học tập AI**: Trợ lý AI cá nhân hóa giúp trả lời câu hỏi
- **Nhận diện giọng nói**: Luyện phát âm cho học ngôn ngữ
- **Công nghệ AR/VR**: Trải nghiệm học tập thực tế ảo tăng cường
- **Chatbot hỗ trợ học tập**: Hỗ trợ 24/7 cho các câu hỏi thường gặp
- **Tự động tạo flashcard**: Trích xuất từ khóa và định nghĩa từ nội dung bài học
- **Tự động tạo câu hỏi kiểm tra**: Phân tích nội dung bài học để tạo câu hỏi
- **Công nghệ OCR**: Nhập nội dung từ hình ảnh và tài liệu quét

#### 8.1.5. Tính năng phân tích và báo cáo
- **Biểu đồ tiến độ học tập**: Biểu đồ trực quan về tiến độ học tập theo thời gian
- **Phân tích thời gian học tập**: Thống kê thời gian học tập theo ngày, tuần, tháng
- **Báo cáo định kỳ**: Báo cáo hàng tuần/hàng tháng về tiến độ
- **Dự đoán thời gian học tập**: Ước tính thời gian cần thiết để hoàn thành mục tiêu
- **Phân tích mẫu quên**: Theo dõi các khái niệm thường bị quên
- **Thống kê chi tiết**: Tỷ lệ đúng/sai trong các bài kiểm tra
- **Xuất báo cáo**: Xuất báo cáo dưới dạng PDF, Excel
- **Biểu đồ thống kê mục tiêu**: Thống kê mục tiêu theo danh mục và trạng thái
- **Biểu đồ hoàn thành mục tiêu**: Theo dõi tỷ lệ hoàn thành mục tiêu theo thời gian
- **Chuỗi ngày liên tiếp**: Theo dõi chuỗi ngày liên tiếp hoàn thành mục tiêu

#### 8.1.6. Tính năng tiện ích và trải nghiệm người dùng
- **Ứng dụng di động**: Phiên bản iOS và Android
- **Chế độ ngoại tuyến**: Tải xuống nội dung để học khi không có kết nối
- **Đồng bộ hóa đa thiết bị**: Học liền mạch trên nhiều thiết bị
- **Tích hợp lịch**: Đồng bộ hóa với Google Calendar/Outlook
- **Xuất mục tiêu sang iCalendar**: Xuất mục tiêu học tập sang định dạng .ics
- **Tích hợp Google Calendar**: Thêm mục tiêu vào Google Calendar
- **Chế độ ban đêm**: Giao diện tối giảm mỏi mắt
- **Tùy chỉnh thông báo**: Chọn loại thông báo nhận được
- **Tích hợp công cụ ghi chú**: Đồng bộ hóa với Notion, Evernote, OneNote

#### 8.1.7. Mở rộng nội dung và đa dạng hóa
- **Thêm nhiều ngôn ngữ**: Mở rộng danh sách ngôn ngữ có thể học
- **Nội dung dạng podcast**: Bài học dạng âm thanh để học khi di chuyển
- **Khóa học video**: Bài giảng video chất lượng cao
- **Tích hợp nguồn học tập mở**: Kết nối với các nguồn học tập mở
- **Hỗ trợ nhiều định dạng**: Đọc và tương tác với PDF, ebook
- **Marketplace nội dung**: Nền tảng cho người tạo nội dung chia sẻ tài liệu
- **Hỗ trợ đa phương pháp học tập**: Tích hợp thêm các phương pháp học tập khác

### 8.2. Cải tiến hiện tại

- **Tối ưu hóa hiệu suất**: Cải thiện tốc độ tải trang
- **Cải thiện giao diện người dùng**: Làm cho giao diện trực quan và dễ sử dụng hơn
- **Mở rộng nội dung học tập**: Thêm nhiều chủ đề và bài học
- **Tích hợp với các nền tảng học tập khác**: Cho phép nhập/xuất dữ liệu

## 9. Tài liệu tham khảo

- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [Spaced Repetition Learning Method](https://en.wikipedia.org/wiki/Spaced_repetition)
- [Active Recall Learning Method](https://en.wikipedia.org/wiki/Active_recall)
- [Kaizen Philosophy](https://en.wikipedia.org/wiki/Kaizen)
- [Zanshin Concept](https://en.wikipedia.org/wiki/Zanshin)
- [Kumon Method](https://en.wikipedia.org/wiki/Kumon)

---

*Memory Bank được tạo bởi [Tên của bạn] - Cập nhật lần cuối: 08/04/2025*
