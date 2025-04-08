"""
Script kiểm tra bảo mật cấu hình Supabase
"""
import os
import sys
import re
import json
from pathlib import Path

# Thêm thư mục gốc của dự án vào sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables directly.")

def check_env_file_security():
    """Kiểm tra bảo mật của file .env"""
    env_file = BASE_DIR / '.env'
    if not env_file.exists():
        print("WARNING: File .env không tồn tại")
        return False

    # Kiểm tra quyền truy cập file
    try:
        import stat
        file_stat = os.stat(env_file)
        permissions = file_stat.st_mode

        # Kiểm tra quyền ghi cho nhóm và người khác
        if permissions & stat.S_IWGRP or permissions & stat.S_IWOTH:
            print("WARNING: File .env có quyền ghi cho nhóm hoặc người khác")
        else:
            print("✓ File .env có quyền truy cập phù hợp")
    except Exception as e:
        print(f"ERROR: Không thể kiểm tra quyền truy cập file .env: {e}")

    # Kiểm tra nội dung file .env
    try:
        with open(env_file, 'r') as f:
            env_content = f.read()

        # Kiểm tra các khóa nhạy cảm
        sensitive_keys = ['SUPABASE_KEY', 'SUPABASE_SECRET', 'DJANGO_SECRET_KEY']
        for key in sensitive_keys:
            pattern = f"{key}=(.+)"
            match = re.search(pattern, env_content)
            if match:
                value = match.group(1).strip()
                if value and value != 'your-supabase-service-role-key-here' and value != 'your-secret-key-here':
                    print(f"✓ {key} đã được cấu hình")
                else:
                    print(f"WARNING: {key} chưa được cấu hình hoặc sử dụng giá trị mặc định")
            else:
                print(f"WARNING: Không tìm thấy {key} trong file .env")

        print("✓ Kiểm tra file .env hoàn tất")
        return True
    except Exception as e:
        print(f"ERROR: Không thể đọc file .env: {e}")
        return False

def check_supabase_key_security():
    """Kiểm tra bảo mật của Supabase key"""
    supabase_key = os.environ.get('SUPABASE_KEY', '')
    if not supabase_key:
        print("ERROR: SUPABASE_KEY không được cấu hình")
        return False

    # Kiểm tra xem key có phải là JWT hợp lệ không
    parts = supabase_key.split('.')
    if len(parts) != 3:
        print("ERROR: SUPABASE_KEY không phải là JWT hợp lệ")
        return False

    try:
        # Giải mã phần payload của JWT
        import base64
        payload = parts[1]
        # Thêm padding nếu cần
        payload += '=' * (4 - len(payload) % 4) if len(payload) % 4 else ''
        decoded = base64.b64decode(payload).decode('utf-8')
        payload_data = json.loads(decoded)

        # Kiểm tra các trường trong payload
        if 'role' in payload_data:
            role = payload_data['role']
            if role == 'anon':
                print("✓ SUPABASE_KEY là anon key (phù hợp cho client)")
            elif role == 'service_role':
                print("WARNING: SUPABASE_KEY là service_role key (chỉ nên sử dụng ở server, không nên để lộ)")
            else:
                print(f"WARNING: SUPABASE_KEY có role không xác định: {role}")
        else:
            print("WARNING: SUPABASE_KEY không có trường 'role'")

        # Kiểm tra thời gian hết hạn
        if 'exp' in payload_data:
            import time
            exp_time = payload_data['exp']
            current_time = int(time.time())
            if exp_time < current_time:
                print(f"ERROR: SUPABASE_KEY đã hết hạn vào {time.ctime(exp_time)}")
            else:
                days_left = (exp_time - current_time) // (24 * 3600)
                print(f"✓ SUPABASE_KEY còn hạn {days_left} ngày")
        else:
            print("WARNING: SUPABASE_KEY không có trường 'exp'")

        print("✓ Kiểm tra SUPABASE_KEY hoàn tất")
        return True
    except Exception as e:
        print(f"ERROR: Không thể phân tích SUPABASE_KEY: {e}")
        return False

def check_database_connection_security():
    """Kiểm tra bảo mật kết nối cơ sở dữ liệu"""
    # Kiểm tra SSL mode
    try:
        import psycopg2

        # Lấy thông tin kết nối từ biến môi trường
        db_host = os.environ.get('SUPABASE_DB_HOST')
        db_port = os.environ.get('SUPABASE_DB_PORT')
        db_name = os.environ.get('SUPABASE_DB_NAME')
        db_user = os.environ.get('SUPABASE_DB_USER')
        db_password = os.environ.get('SUPABASE_DB_PASSWORD')

        if not all([db_host, db_port, db_name, db_user, db_password]):
            print("ERROR: Thiếu thông tin kết nối cơ sở dữ liệu")
            return False

        # Thử kết nối với sslmode=require
        try:
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                dbname=db_name,
                user=db_user,
                password=db_password,
                sslmode='require'
            )
            conn.close()
            print("✓ Kết nối cơ sở dữ liệu với SSL thành công")
        except Exception as e:
            print(f"ERROR: Không thể kết nối cơ sở dữ liệu với SSL: {e}")
            return False

        # Kiểm tra mật khẩu cơ sở dữ liệu
        if not db_password:
            print("ERROR: Không có mật khẩu cơ sở dữ liệu")
        elif len(db_password) < 8:
            print("WARNING: Mật khẩu cơ sở dữ liệu quá ngắn")
        else:
            print("✓ Mật khẩu cơ sở dữ liệu có độ dài phù hợp")

        print("✓ Kiểm tra bảo mật kết nối cơ sở dữ liệu hoàn tất")
        return True
    except ImportError:
        print("ERROR: Không thể import psycopg2. Vui lòng cài đặt: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"ERROR: Không thể kiểm tra bảo mật kết nối cơ sở dữ liệu: {e}")
        return False

def check_settings_security():
    """Kiểm tra bảo mật trong file settings.py"""
    settings_file = BASE_DIR / 'learning_platform' / 'settings.py'
    if not settings_file.exists():
        print("ERROR: File settings.py không tồn tại")
        return False

    try:
        with open(settings_file, 'r') as f:
            settings_content = f.read()

        # Kiểm tra DEBUG mode
        debug_pattern = r"DEBUG\s*=\s*(.+)"
        debug_match = re.search(debug_pattern, settings_content)
        if debug_match:
            debug_value = debug_match.group(1).strip()
            if 'True' in debug_value and 'os.environ.get' not in debug_value:
                print("WARNING: DEBUG = True được hardcode trong settings.py")
            else:
                print("✓ DEBUG được cấu hình đúng cách")

        # Kiểm tra SECRET_KEY
        secret_key_pattern = r"SECRET_KEY\s*=\s*(.+)"
        secret_key_match = re.search(secret_key_pattern, settings_content)
        if secret_key_match:
            secret_key_value = secret_key_match.group(1).strip()
            if '"' in secret_key_value and 'os.environ.get' not in secret_key_value:
                print("WARNING: SECRET_KEY được hardcode trong settings.py")
            else:
                print("✓ SECRET_KEY được cấu hình đúng cách")

        # Kiểm tra cấu hình cơ sở dữ liệu
        if 'sslmode' in settings_content and 'require' in settings_content:
            print("✓ SSL mode được cấu hình cho kết nối cơ sở dữ liệu")
        else:
            print("WARNING: Không tìm thấy cấu hình SSL mode cho kết nối cơ sở dữ liệu")

        # Kiểm tra cấu hình bảo mật khác
        security_features = [
            ('SECURE_SSL_REDIRECT', 'Chuyển hướng SSL'),
            ('SESSION_COOKIE_SECURE', 'Cookie phiên bảo mật'),
            ('CSRF_COOKIE_SECURE', 'Cookie CSRF bảo mật'),
            ('SECURE_HSTS_SECONDS', 'HTTP Strict Transport Security'),
            ('SECURE_CONTENT_TYPE_NOSNIFF', 'X-Content-Type-Options nosniff'),
            ('SECURE_BROWSER_XSS_FILTER', 'XSS Protection')
        ]

        for feature, description in security_features:
            if feature in settings_content and 'True' in settings_content.split(feature)[1].split('\n')[0]:
                print(f"✓ {description} được bật")
            else:
                print(f"WARNING: {description} có thể chưa được bật")

        print("✓ Kiểm tra bảo mật settings.py hoàn tất")
        return True
    except Exception as e:
        print(f"ERROR: Không thể kiểm tra bảo mật settings.py: {e}")
        return False

def run_security_checks():
    """Chạy tất cả các kiểm tra bảo mật"""
    print("=== KIỂM TRA BẢO MẬT CẤU HÌNH SUPABASE ===")

    checks = [
        ("Kiểm tra file .env", check_env_file_security),
        ("Kiểm tra Supabase key", check_supabase_key_security),
        ("Kiểm tra kết nối cơ sở dữ liệu", check_database_connection_security),
        ("Kiểm tra file settings.py", check_settings_security)
    ]

    results = []
    for name, check_func in checks:
        print(f"\n--- {name} ---")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"ERROR: Lỗi không xác định khi chạy kiểm tra: {e}")
            results.append(False)

    # Tổng kết
    print("\n=== KẾT QUẢ KIỂM TRA BẢO MẬT ===")
    for i, (name, _) in enumerate(checks):
        status = "PASS" if results[i] else "FAIL"
        print(f"{name}: {status}")

    if all(results):
        print("\nTất cả các kiểm tra bảo mật đều PASS!")
    else:
        print("\nMột số kiểm tra bảo mật FAIL. Vui lòng kiểm tra lại cấu hình.")

    # Đề xuất cải thiện
    print("\n=== ĐỀ XUẤT CẢI THIỆN BẢO MẬT ===")
    print("1. Sử dụng mật khẩu mạnh và duy nhất cho cơ sở dữ liệu")
    print("2. Không sử dụng service_role key trong môi trường client")
    print("3. Đảm bảo tất cả các biến nhạy cảm được lưu trong biến môi trường")
    print("4. Bật tất cả các tính năng bảo mật trong settings.py cho môi trường production")
    print("5. Giới hạn quyền truy cập vào cơ sở dữ liệu Supabase bằng Row Level Security (RLS)")
    print("6. Thường xuyên cập nhật các thư viện và dependencies")

if __name__ == "__main__":
    run_security_checks()
