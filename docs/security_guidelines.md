# Hướng dẫn bảo mật cho dự án

## Tổng quan

Tài liệu này cung cấp hướng dẫn về cách bảo vệ thông tin nhạy cảm trong dự án và đảm bảo rằng không có thông tin nhạy cảm nào bị đẩy lên kho lưu trữ Git.

## Thông tin nhạy cảm

Thông tin nhạy cảm bao gồm, nhưng không giới hạn ở:

- Khóa API (API keys)
- Mật khẩu
- Khóa bí mật (Secret keys)
- Token xác thực
- Thông tin kết nối cơ sở dữ liệu
- Chứng chỉ SSL/TLS
- Khóa riêng tư (Private keys)
- Thông tin cá nhân của người dùng

## Quy tắc bảo mật

### 1. Sử dụng biến môi trường

- **KHÔNG BAO GIỜ** hardcode thông tin nhạy cảm trong mã nguồn
- Luôn sử dụng biến môi trường cho thông tin nhạy cảm
- Sử dụng file `.env` để lưu trữ biến môi trường cục bộ
- Đảm bảo file `.env` được liệt kê trong `.gitignore`

Ví dụ sử dụng biến môi trường trong Python:

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Tải biến môi trường từ file .env

# Sử dụng biến môi trường
api_key = os.environ.get('API_KEY')
database_url = os.environ.get('DATABASE_URL')
```

### 2. Sử dụng file .env.example

- Tạo file `.env.example` để làm mẫu cho các biến môi trường cần thiết
- **KHÔNG** đưa giá trị thực tế vào file `.env.example`
- Commit file `.env.example` vào Git để người khác biết cần thiết lập những biến môi trường nào

Ví dụ nội dung file `.env.example`:

```
# API Keys
API_KEY=your-api-key-here

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=your-password-here

# Security
SECRET_KEY=your-secret-key-here
```

### 3. Kiểm tra thông tin nhạy cảm trước khi commit

- Sử dụng script `scripts/check_sensitive_info.py` để kiểm tra thông tin nhạy cảm trước khi commit
- Script này sẽ tự động chạy thông qua Git pre-commit hook
- Nếu tìm thấy thông tin nhạy cảm, commit sẽ bị hủy

Để chạy kiểm tra thủ công:

```bash
python scripts/check_sensitive_info.py
```

### 4. Xử lý khi thông tin nhạy cảm đã bị commit

Nếu thông tin nhạy cảm đã vô tình bị commit vào Git:

1. **Thay đổi thông tin nhạy cảm ngay lập tức** (đổi mật khẩu, tạo khóa API mới, v.v.)
2. Sử dụng `git filter-branch` hoặc [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) để xóa thông tin nhạy cảm khỏi lịch sử Git
3. Thông báo cho team về sự cố và các bước đã thực hiện

## Công cụ bảo mật

### 1. Git pre-commit hook

Dự án đã cài đặt Git pre-commit hook để tự động kiểm tra thông tin nhạy cảm trước khi commit. Hook này sẽ:

- Chạy script `scripts/check_sensitive_info.py` để tìm thông tin nhạy cảm trong mã nguồn
- Kiểm tra xem file `.env` có đang được commit không
- Hủy commit nếu tìm thấy vấn đề bảo mật

### 2. Script kiểm tra thông tin nhạy cảm

Script `scripts/check_sensitive_info.py` sẽ quét mã nguồn để tìm các mẫu thông tin nhạy cảm như:

- API keys, tokens, credentials
- Chuỗi kết nối cơ sở dữ liệu
- Khóa AWS
- Khóa riêng tư và chứng chỉ

## Tài liệu tham khảo

- [OWASP Cheat Sheet: Environment Variables](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html#rule-4-use-environment-variables-for-secrets-and-configuration)
- [Django Security Best Practices](https://docs.djangoproject.com/en/stable/topics/security/)
- [Git - Removing Sensitive Data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
