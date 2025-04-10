# Tech Context - Nền Tảng Học Tập

## Công nghệ cốt lõi
### Backend
- **Django**: Framework web Python, cung cấp ORM, hệ thống xác thực, admin interface
- **Python**: Ngôn ngữ lập trình chính cho backend
- **PostgreSQL**: Hệ quản trị cơ sở dữ liệu quan hệ (thông qua Supabase)
- **Supabase**: Nền tảng backend-as-a-service, cung cấp PostgreSQL, authentication, storage

### Frontend
- **Django Templates**: Hệ thống template của Django
- **Bootstrap**: Framework CSS cho giao diện responsive
- **HTMX**: Thư viện JavaScript cho AJAX, CSS Transitions, WebSockets
- **Alpine.js**: Framework JavaScript nhẹ cho tương tác phía client

### Công cụ bổ sung
- **django-summernote**: Rich text editor
- **xhtml2pdf**: Tạo file PDF từ HTML
- **Tesseract OCR**: Nhận dạng ký tự quang học
- **django-crispy-forms**: Tạo form đẹp và dễ sử dụng

## Môi trường phát triển
### Yêu cầu hệ thống
- Python 3.8+
- PostgreSQL 12+
- Node.js (cho các công cụ frontend)
- Git

### Cài đặt môi trường
```bash
# Tạo và kích hoạt môi trường ảo
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Thiết lập biến môi trường
# Tạo file .env từ .env.example

# Chạy migrations
python manage.py migrate

# Tạo superuser
python manage.py createsuperuser

# Chạy server
python manage.py runserver
```

### Cấu trúc thư mục
```
learning_platform/
├── accounts/            # Ứng dụng quản lý người dùng
├── content/             # Ứng dụng quản lý nội dung học tập
├── flashcards/          # Ứng dụng flashcards
├── quizzes/             # Ứng dụng bài kiểm tra
├── memory_bank/         # Ứng dụng quản lý ghi nhớ
├── advanced_learning/   # Ứng dụng học tập nâng cao
├── notifications/       # Ứng dụng thông báo
├── learning_goals/      # Ứng dụng mục tiêu học tập
├── achievements/        # Ứng dụng thành tích
├── personalization/     # Ứng dụng cá nhân hóa
├── ai_assistant/        # Ứng dụng trợ lý AI
├── learning_chatbot/    # Ứng dụng chatbot
├── learning_analytics/  # Ứng dụng phân tích học tập
├── ocr_app/             # Ứng dụng OCR
├── note_integration_app/# Ứng dụng tích hợp ghi chú
├── learning_platform/   # Thư mục chính của dự án
│   ├── settings.py      # Cấu hình dự án
│   ├── urls.py          # URL routing chính
│   ├── wsgi.py          # WSGI configuration
│   └── asgi.py          # ASGI configuration
├── static/              # Static files (CSS, JS, images)
├── media/               # User-uploaded files
├── templates/           # Global templates
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables
```

## Cấu hình và biến môi trường
### Biến môi trường chính
- `DJANGO_DEBUG`: Chế độ debug (True/False)
- `ALLOWED_HOSTS`: Danh sách hosts được phép
- `SECRET_KEY`: Django secret key
- `SUPABASE_DB_USER`: Tên người dùng Supabase
- `SUPABASE_DB_PASSWORD`: Mật khẩu Supabase
- `SUPABASE_DB_HOST`: Host Supabase
- `SUPABASE_DB_PORT`: Port Supabase (mặc định: 5432)
- `SUPABASE_DB_NAME`: Tên database Supabase (mặc định: postgres)
- `SUPABASE_URL`: URL Supabase API
- `SUPABASE_KEY`: Khóa API Supabase
- `SUPABASE_SECRET`: Khóa bí mật Supabase

### Cấu hình Django
```python
# Cấu hình cơ sở dữ liệu
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('SUPABASE_DB_NAME', 'postgres'),
        'USER': os.environ.get('SUPABASE_DB_USER'),
        'PASSWORD': os.environ.get('SUPABASE_DB_PASSWORD'),
        'HOST': os.environ.get('SUPABASE_DB_HOST'),
        'PORT': os.environ.get('SUPABASE_DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
            'options': f'-c search_path={os.environ.get("SUPABASE_DB_SCHEMA", "public")}',
        },
    }
}

# Cấu hình static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Cấu hình media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## Tích hợp bên thứ ba
### Supabase
- **Database**: PostgreSQL database
- **Authentication**: User authentication
- **Storage**: File storage
- **Realtime**: Realtime subscriptions

### Notion API
- Tích hợp với Notion để đồng bộ ghi chú

### Microsoft Graph API
- Tích hợp với OneNote để đồng bộ ghi chú

### Tesseract OCR
- Nhận dạng văn bản từ hình ảnh

## Bảo mật
### Các biện pháp bảo mật
- **HTTPS**: Bảo mật kết nối
- **CSRF Protection**: Bảo vệ chống tấn công CSRF
- **XSS Protection**: Bảo vệ chống tấn công XSS
- **SQL Injection Protection**: Bảo vệ chống tấn công SQL Injection
- **Password Hashing**: Mã hóa mật khẩu
- **Permission System**: Hệ thống phân quyền

### Xử lý dữ liệu nhạy cảm
- Sử dụng biến môi trường cho thông tin nhạy cảm
- Không lưu thông tin nhạy cảm trong mã nguồn
- Sử dụng pre-commit hook để kiểm tra thông tin nhạy cảm

## Hiệu suất
### Tối ưu hóa
- **Database Indexing**: Tạo index cho các trường thường xuyên truy vấn
- **Query Optimization**: Tối ưu hóa các truy vấn database
- **Caching**: Sử dụng cache cho dữ liệu ít thay đổi
- **Lazy Loading**: Tải dữ liệu khi cần thiết
- **Pagination**: Phân trang cho dữ liệu lớn

### Monitoring
- **Django Debug Toolbar**: Theo dõi hiệu suất trong môi trường phát triển
- **Logging**: Ghi log cho các sự kiện quan trọng

## Triển khai
### Quy trình triển khai
1. **Development**: Phát triển trên máy local
2. **Testing**: Kiểm thử tự động và thủ công
3. **Staging**: Triển khai lên môi trường staging
4. **Production**: Triển khai lên môi trường production

### CI/CD
- **Pre-commit Hooks**: Kiểm tra code trước khi commit
- **Automated Testing**: Kiểm thử tự động
- **Deployment Automation**: Tự động hóa triển khai

## Ràng buộc kỹ thuật
- **Browser Support**: Hỗ trợ các trình duyệt hiện đại (Chrome, Firefox, Safari, Edge)
- **Responsive Design**: Hỗ trợ các thiết bị di động và desktop
- **Accessibility**: Tuân thủ WCAG 2.1 AA
- **Performance**: Thời gian tải trang < 3 giây
- **Scalability**: Hỗ trợ tối thiểu 10,000 người dùng đồng thời
