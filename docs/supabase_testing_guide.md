# Hướng dẫn kiểm tra kết nối và bảo mật Supabase

## Giới thiệu

Tài liệu này hướng dẫn cách sử dụng các công cụ kiểm tra kết nối và bảo mật Supabase trong dự án Django. Các công cụ này giúp bạn xác minh rằng kết nối Supabase hoạt động đúng cách và được cấu hình an toàn.

## Cài đặt

Trước khi sử dụng các công cụ kiểm tra, hãy đảm bảo bạn đã cài đặt tất cả các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

## Sử dụng công cụ kiểm tra

### Chạy tất cả các kiểm tra

Để chạy tất cả các kiểm tra (kết nối, bảo mật và hiệu suất), sử dụng lệnh:

```bash
python check_supabase.py --all
```

hoặc đơn giản là:

```bash
python check_supabase.py
```

### Chỉ chạy kiểm tra kết nối

Để chỉ kiểm tra kết nối đến Supabase:

```bash
python check_supabase.py --connection
```

Kiểm tra này sẽ:
- Xác minh các biến môi trường cần thiết đã được cấu hình
- Kiểm tra kết nối đến Supabase API
- Kiểm tra kết nối đến Supabase PostgreSQL
- Kiểm tra cấu hình bảo mật
- Kiểm tra xử lý lỗi

### Chỉ chạy kiểm tra bảo mật

Để chỉ kiểm tra bảo mật của cấu hình Supabase:

```bash
python check_supabase.py --security
```

Kiểm tra này sẽ:
- Kiểm tra bảo mật của file .env
- Phân tích Supabase key để xác định loại và thời hạn
- Kiểm tra bảo mật kết nối cơ sở dữ liệu
- Kiểm tra cấu hình bảo mật trong file settings.py

### Chỉ chạy kiểm tra hiệu suất

Để chỉ kiểm tra hiệu suất của kết nối Supabase:

```bash
python check_supabase.py --performance
```

Kiểm tra này sẽ:
- Đo độ trễ của Supabase API
- Đo độ trễ của kết nối cơ sở dữ liệu
- Kiểm tra khả năng xử lý kết nối đồng thời

## Giải thích kết quả

### Kết quả kiểm tra kết nối

- **PASS**: Kết nối thành công và hoạt động đúng cách
- **FAIL**: Có vấn đề với kết nối, xem thông báo lỗi để biết chi tiết

### Kết quả kiểm tra bảo mật

- **PASS**: Cấu hình bảo mật đáp ứng các tiêu chuẩn tối thiểu
- **FAIL**: Có vấn đề bảo mật cần được giải quyết
- **WARNING**: Có cảnh báo bảo mật cần được xem xét

### Kết quả kiểm tra hiệu suất

- **Độ trễ API**: Thời gian phản hồi của Supabase API
- **Độ trễ cơ sở dữ liệu**: Thời gian phản hồi của truy vấn cơ sở dữ liệu
- **Kết nối đồng thời**: Khả năng xử lý nhiều kết nối cùng lúc

## Các vấn đề thường gặp và cách khắc phục

### Không thể kết nối đến Supabase API

- Kiểm tra SUPABASE_URL và SUPABASE_KEY trong file .env
- Đảm bảo bạn đang sử dụng anon key hoặc service_role key đúng
- Kiểm tra kết nối internet

### Không thể kết nối đến Supabase PostgreSQL

- Kiểm tra thông tin kết nối cơ sở dữ liệu trong file .env
- Đảm bảo IP của bạn được phép truy cập vào cơ sở dữ liệu
- Kiểm tra tường lửa và cấu hình mạng

### Cảnh báo bảo mật

- **Sử dụng service_role key**: Chỉ sử dụng service_role key ở phía server, không bao giờ ở phía client
- **Mật khẩu yếu**: Thay đổi mật khẩu cơ sở dữ liệu thành một mật khẩu mạnh và duy nhất
- **Thiếu SSL**: Luôn sử dụng SSL (sslmode=require) khi kết nối đến cơ sở dữ liệu

### Hiệu suất kém

- **Độ trễ cao**: Kiểm tra vị trí máy chủ Supabase và cân nhắc sử dụng region gần hơn
- **Kết nối đồng thời thất bại**: Tăng giới hạn kết nối hoặc sử dụng connection pooling
- **Truy vấn chậm**: Tối ưu hóa truy vấn và sử dụng chỉ mục

## Các đề xuất bảo mật

1. **Sử dụng biến môi trường**: Lưu tất cả các khóa và thông tin nhạy cảm trong biến môi trường
2. **Row Level Security (RLS)**: Cấu hình RLS trong Supabase để kiểm soát quyền truy cập dữ liệu
3. **Phân quyền**: Sử dụng hệ thống phân quyền của Supabase để giới hạn quyền truy cập
4. **Mã hóa dữ liệu nhạy cảm**: Mã hóa dữ liệu nhạy cảm trước khi lưu vào cơ sở dữ liệu
5. **Giám sát**: Bật tính năng giám sát và ghi nhật ký để phát hiện các hoạt động đáng ngờ
6. **Cập nhật thường xuyên**: Cập nhật thường xuyên các thư viện và dependencies

## Tài liệu tham khảo

- [Supabase Documentation](https://supabase.io/docs)
- [Supabase Security Best Practices](https://supabase.io/docs/guides/auth/security)
- [PostgreSQL SSL Documentation](https://www.postgresql.org/docs/current/ssl-tcp.html)
- [Django Security Best Practices](https://docs.djangoproject.com/en/stable/topics/security/)
