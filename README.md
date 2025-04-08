# Nền Tảng Học Tập

Nền Tảng Học Tập là một ứng dụng web được xây dựng bằng Django, giúp người dùng học tập hiệu quả với các phương pháp khoa học như Active Recall, Spaced Repetition, Kumon, Kaizen, và Zanshin.

## Tính Năng

- **Đa dạng chủ đề học tập**: Tiếng Anh, Tiếng Trung, Python, Java, Toán học, và nhiều chủ đề khác.
- **Active Recall**: Học tập chủ động thông qua flashcards.
- **Spaced Repetition**: Hệ thống lên lịch ôn tập thông minh.
- **Bài kiểm tra**: Kiểm tra kiến thức với các bài kiểm tra tương tác.
- **Theo dõi tiến độ**: Theo dõi tiến độ học tập và thời gian học.
- **Hồ sơ người dùng**: Quản lý thông tin cá nhân và mục tiêu học tập.
- **Memory Bank**: Ngân hàng ghi nhớ để lưu trữ và quản lý các ghi nhớ, ý tưởng, và kiến thức quan trọng.

## Cài Đặt

### Yêu Cầu

- Python 3.8+
- Django 5.2+
- PostgreSQL (Supabase)
- Các thư viện khác được liệt kê trong `requirements.txt`

### Các Bước Cài Đặt

1. Clone repository:
   ```
   git clone https://github.com/yourusername/learning-platform.git
   cd learning-platform
   ```

2. Tạo môi trường ảo và kích hoạt:
   ```
   python -m venv venv
   source venv/bin/activate  # Trên Linux/Mac
   venv\Scripts\activate     # Trên Windows
   ```

3. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```

4. Cài đặt Git hooks để bảo vệ thông tin nhạy cảm:
   - Trên Windows:
     ```
     scripts\install_hooks.bat
     ```
   - Trên Linux/Mac:
     ```
     bash scripts/install_hooks.sh
     ```

5. Cấu hình kết nối Supabase:
   - Sử dụng script tự động để tạo file `.env`:
     ```
     python scripts/setup_env.py
     ```
   - Hoặc sao chép file `.env.example` thành `.env` và cập nhật thủ công
   - Xem hướng dẫn chi tiết tại `docs/supabase_integration.md`
   - **Lưu ý**: Không bao giờ commit file `.env` lên Git (Git hooks sẽ ngăn chặn điều này)

6. Tạo cơ sở dữ liệu:
   ```
   python manage.py migrate
   ```

7. Tạo tài khoản admin:
   ```
   python manage.py createsuperuser
   ```

8. Tạo dữ liệu mẫu (tùy chọn):
   ```
   python sample_data.py
   ```

9. Chạy máy chủ phát triển:
   ```
   python manage.py runserver
   ```

10. Truy cập ứng dụng tại http://127.0.0.1:8000/

## Cấu Trúc Dự Án

- **accounts**: Quản lý người dùng, hồ sơ, và tiến độ học tập.
- **content**: Quản lý chủ đề, bài học, và nội dung học tập.
- **flashcards**: Hệ thống flashcard và Spaced Repetition.
- **quizzes**: Hệ thống bài kiểm tra và đánh giá.
- **memory_bank**: Ngân hàng ghi nhớ để lưu trữ và quản lý các ghi nhớ, ý tưởng, và kiến thức quan trọng.
- **templates**: Các template HTML cho giao diện người dùng.
- **static**: CSS, JavaScript, và các tài nguyên tĩnh khác.

## Phương Pháp Học Tập

### Active Recall
Thay vì đọc đi đọc lại thông tin, Active Recall khuyến khích bạn chủ động truy xuất thông tin từ trí nhớ. Điều này tạo ra các kết nối thần kinh mạnh mẽ hơn và cải thiện khả năng ghi nhớ dài hạn.

### Spaced Repetition
Hệ thống lên lịch ôn tập thông minh, giúp bạn ôn tập đúng thời điểm trước khi quên. Phương pháp này tối ưu hóa thời gian học tập và tăng cường trí nhớ dài hạn.

### Kumon Method
Chia nhỏ kiến thức thành các phần dễ tiếp thu, khuyến khích ôn tập hàng ngày thay vì học dồn. Phương pháp này giúp xây dựng nền tảng vững chắc trước khi tiến đến các khái niệm phức tạp hơn.

### Kaizen
Cải thiện liên tục mỗi ngày với mục tiêu nhỏ. Dành 6 phút mỗi ngày để ôn tập và cải thiện kỹ năng của bạn. Sự tiến bộ nhỏ mỗi ngày sẽ tạo nên sự khác biệt lớn theo thời gian.

### Zanshin
Tập trung tối đa vào việc học, loại bỏ các yếu tố gây xao nhãng. Phương pháp này giúp tăng cường hiệu quả học tập và tiết kiệm thời gian.

## Đóng Góp

Chúng tôi rất hoan nghênh đóng góp từ cộng đồng! Nếu bạn muốn đóng góp, vui lòng:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/amazing-feature`)
3. Commit các thay đổi của bạn (`git commit -m 'Add some amazing feature'`)
4. Push lên branch (`git push origin feature/amazing-feature`)
5. Mở Pull Request

## Giấy Phép

Dự án này được cấp phép theo giấy phép MIT - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## Liên Hệ

Nếu bạn có bất kỳ câu hỏi hoặc góp ý nào, vui lòng liên hệ với chúng tôi qua email: contact@learning-platform.com
