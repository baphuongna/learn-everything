# Hướng dẫn tích hợp Supabase với Django

## Giới thiệu

Tài liệu này hướng dẫn cách tích hợp Supabase với dự án Django. Supabase là một nền tảng Backend-as-a-Service (BaaS) mã nguồn mở, cung cấp các dịch vụ như cơ sở dữ liệu PostgreSQL, xác thực, lưu trữ file, và API tự động.

## Cài đặt

Để sử dụng Supabase trong dự án Django, bạn cần cài đặt các thư viện sau:

```bash
pip install supabase psycopg2-binary dj-database-url
```

Hoặc cài đặt từ file requirements.txt:

```bash
pip install -r requirements.txt
```

## Cấu hình

### 1. Cấu hình biến môi trường

Tạo file `.env` từ file `.env.example` và cập nhật các thông tin Supabase:

```
# Cấu hình Supabase API
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SECRET=your-supabase-service-role-key

# Cấu hình PostgreSQL - Connection Pooler
SUPABASE_DB_HOST=aws-0-region-code.pooler.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres.your-project-id
SUPABASE_DB_PASSWORD=your-database-password
SUPABASE_DB_SCHEMA=public
```

**Lưu ý quan trọng:**
- `SUPABASE_DB_USER` cần được đặt theo định dạng `postgres.{project-id}` khi sử dụng Connection Pooler
- `SUPABASE_DB_PASSWORD` là mật khẩu cơ sở dữ liệu PostgreSQL, có thể tìm thấy trong phần cài đặt dự án Supabase
- `SUPABASE_DB_HOST` sử dụng địa chỉ Connection Pooler của Supabase (ví dụ: aws-0-ap-southeast-1.pooler.supabase.com)

Dự án đã được cấu hình để sử dụng kết nối qua Connection Pooler, giúp đảm bảo kết nối ổn định trong mọi môi trường (cả IPv4 và IPv6):

### 2. Cấu hình cơ sở dữ liệu

Dự án đã được cấu hình để sử dụng Supabase PostgreSQL trong môi trường production và SQLite trong môi trường phát triển. Cấu hình này được định nghĩa trong file `settings.py`.

## Sử dụng Supabase API

### 1. Sử dụng Supabase Client

Dự án cung cấp một lớp `SupabaseClient` trong `utils/supabase_client.py` để tương tác với Supabase API. Đây là một singleton class, vì vậy bạn có thể import và sử dụng nó ở bất kỳ đâu trong dự án:

```python
from utils.supabase_client import supabase

# Lấy dữ liệu từ bảng
response = supabase.get_data('table_name')
data = response.data

# Thêm dữ liệu vào bảng
new_data = {'column1': 'value1', 'column2': 'value2'}
response = supabase.insert_data('table_name', new_data)

# Cập nhật dữ liệu
update_data = {'column1': 'new_value'}
response = supabase.update_data('table_name', update_data, 'id', 1)

# Xóa dữ liệu
response = supabase.delete_data('table_name', 'id', 1)
```

### 2. Sử dụng trong Django Views

Ví dụ về cách sử dụng Supabase trong Django views:

```python
from django.shortcuts import render
from utils.supabase_client import supabase

def product_list(request):
    response = supabase.get_data('products')
    products = response.data
    return render(request, 'products/list.html', {'products': products})
```

### 3. Sử dụng với Django Models

Nếu bạn muốn sử dụng Django ORM với Supabase PostgreSQL, bạn có thể sử dụng cấu hình cơ sở dữ liệu đã được thiết lập. Django sẽ tự động kết nối với Supabase PostgreSQL và bạn có thể sử dụng các model như bình thường:

```python
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name
```

## Xác thực với Supabase

Supabase cung cấp hệ thống xác thực mạnh mẽ. Để sử dụng xác thực Supabase với Django:

```python
from utils.supabase_client import supabase

def register_user(email, password):
    try:
        response = supabase.client.auth.sign_up({
            "email": email,
            "password": password,
        })
        return response
    except Exception as e:
        print(f"Lỗi khi đăng ký: {e}")
        return None

def login_user(email, password):
    try:
        response = supabase.client.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        return response
    except Exception as e:
        print(f"Lỗi khi đăng nhập: {e}")
        return None
```

## Lưu trữ file với Supabase Storage

Supabase cung cấp dịch vụ lưu trữ file. Để sử dụng:

```python
from utils.supabase_client import supabase

def upload_file(bucket_name, file_path, file_content):
    try:
        response = supabase.client.storage.from_(bucket_name).upload(
            file_path,
            file_content
        )
        return response
    except Exception as e:
        print(f"Lỗi khi tải lên file: {e}")
        return None

def get_file_url(bucket_name, file_path):
    try:
        url = supabase.client.storage.from_(bucket_name).get_public_url(file_path)
        return url
    except Exception as e:
        print(f"Lỗi khi lấy URL file: {e}")
        return None
```

## Xử lý lỗi

Khi làm việc với Supabase API, luôn đảm bảo xử lý lỗi đúng cách:

```python
try:
    response = supabase.get_data('table_name')
    if response.data:
        # Xử lý dữ liệu
        pass
    else:
        # Xử lý trường hợp không có dữ liệu
        pass
except Exception as e:
    # Xử lý lỗi
    print(f"Lỗi khi lấy dữ liệu: {e}")
```

## Kiểm tra kết nối

Dự án đã bao gồm script `simple_supabase_test.py` để kiểm tra kết nối với Supabase. Bạn có thể chạy script này để kiểm tra cả kết nối API và kết nối PostgreSQL:

```bash
python simple_supabase_test.py
```

Kết quả mong đợi:

```
Kiểm tra kết nối Supabase API...
Thử truy vấn bảng...
[Các bảng có thể không tồn tại nếu cơ sở dữ liệu mới]

Thử sử dụng Storage API...
Danh sách buckets: []

Thông tin kết nối PostgreSQL:
Kết nối PostgreSQL thành công!
Phiên bản PostgreSQL: PostgreSQL 15.8 on aarch64-unknown-linux-gnu, compiled by gcc (GCC) 13.2.0, 64-bit
```

Bạn cũng có thể kiểm tra kết nối trực tiếp bằng cách sử dụng mã sau:

```python
import psycopg2

# Kết nối qua Connection Pooler
conn = psycopg2.connect(
    host="aws-0-region-code.pooler.supabase.com",
    database="postgres",
    user="postgres.your-project-id",
    password="your-database-password",
    port="5432",
    sslmode="require"
)

# Kiểm tra kết nối
cursor = conn.cursor()
cursor.execute("SELECT version();")
version = cursor.fetchone()
print(f"PostgreSQL version: {version[0]}")

# Đóng kết nối
cursor.close()
conn.close()
```

## Tài liệu tham khảo

- [Supabase Documentation](https://supabase.io/docs)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
