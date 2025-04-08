"""
Script kiểm tra kết nối và bảo mật của Supabase
"""
import os
import sys
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

# Kiểm tra các biến môi trường cần thiết
def check_environment_variables():
    """Kiểm tra các biến môi trường cần thiết cho Supabase"""
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SUPABASE_DB_USER',
        'SUPABASE_DB_PASSWORD',
        'SUPABASE_DB_HOST',
        'SUPABASE_DB_PORT',
        'SUPABASE_DB_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"ERROR: Thiếu các biến môi trường sau: {', '.join(missing_vars)}")
        return False
    
    print("✓ Tất cả biến môi trường cần thiết đã được cấu hình")
    return True

# Kiểm tra kết nối đến Supabase API
def test_supabase_api_connection():
    """Kiểm tra kết nối đến Supabase API"""
    try:
        from utils.supabase_client import supabase
        
        # Thử lấy dữ liệu từ bảng _schema.tables (bảng hệ thống)
        response = supabase.client.table('_schema.tables').select('*').limit(1).execute()
        
        if response.data:
            print("✓ Kết nối đến Supabase API thành công")
            return True
        else:
            print("WARNING: Kết nối đến Supabase API thành công nhưng không có dữ liệu trả về")
            return True
    except Exception as e:
        print(f"ERROR: Không thể kết nối đến Supabase API: {e}")
        return False

# Kiểm tra kết nối đến Supabase PostgreSQL
def test_postgres_connection():
    """Kiểm tra kết nối đến Supabase PostgreSQL"""
    try:
        import psycopg2
        
        # Lấy thông tin kết nối từ biến môi trường
        db_host = os.environ.get('SUPABASE_DB_HOST')
        db_port = os.environ.get('SUPABASE_DB_PORT')
        db_name = os.environ.get('SUPABASE_DB_NAME')
        db_user = os.environ.get('SUPABASE_DB_USER')
        db_password = os.environ.get('SUPABASE_DB_PASSWORD')
        
        # Kết nối đến PostgreSQL
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password,
            sslmode='require'
        )
        
        # Tạo cursor và thực hiện truy vấn đơn giản
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        # Đóng kết nối
        cursor.close()
        conn.close()
        
        print(f"✓ Kết nối đến Supabase PostgreSQL thành công: {version[0]}")
        return True
    except Exception as e:
        print(f"ERROR: Không thể kết nối đến Supabase PostgreSQL: {e}")
        return False

# Kiểm tra cấu hình bảo mật
def check_security_config():
    """Kiểm tra cấu hình bảo mật của Supabase"""
    # Kiểm tra SUPABASE_KEY
    supabase_key = os.environ.get('SUPABASE_KEY', '')
    if not supabase_key:
        print("ERROR: SUPABASE_KEY không được cấu hình")
        return False
    
    # Kiểm tra xem key có phải là anon key hay service_role key
    if 'role":"anon"' in supabase_key:
        print("✓ SUPABASE_KEY là anon key (phù hợp cho client)")
    elif 'role":"service_role"' in supabase_key:
        print("WARNING: SUPABASE_KEY là service_role key (chỉ nên sử dụng ở server, không nên để lộ)")
    else:
        print("WARNING: Không thể xác định loại SUPABASE_KEY")
    
    # Kiểm tra cấu hình SSL
    db_host = os.environ.get('SUPABASE_DB_HOST', '')
    if not db_host.endswith('.supabase.co'):
        print("WARNING: SUPABASE_DB_HOST không phải là domain của Supabase")
    
    print("✓ Kiểm tra cấu hình bảo mật hoàn tất")
    return True

# Kiểm tra xử lý lỗi trong Supabase client
def check_error_handling():
    """Kiểm tra xử lý lỗi trong Supabase client"""
    try:
        from utils.supabase_client import supabase
        
        # Thử truy cập một bảng không tồn tại
        try:
            response = supabase.get_data('non_existent_table')
            print("ERROR: Không có xử lý lỗi khi truy cập bảng không tồn tại")
            return False
        except Exception as e:
            print(f"✓ Xử lý lỗi khi truy cập bảng không tồn tại: {e}")
        
        return True
    except Exception as e:
        print(f"ERROR: Không thể kiểm tra xử lý lỗi: {e}")
        return False

# Hàm chính để chạy tất cả các kiểm tra
def run_all_tests():
    """Chạy tất cả các kiểm tra"""
    print("=== KIỂM TRA KẾT NỐI VÀ BẢO MẬT SUPABASE ===")
    
    tests = [
        ("Kiểm tra biến môi trường", check_environment_variables),
        ("Kiểm tra kết nối Supabase API", test_supabase_api_connection),
        ("Kiểm tra kết nối PostgreSQL", test_postgres_connection),
        ("Kiểm tra cấu hình bảo mật", check_security_config),
        ("Kiểm tra xử lý lỗi", check_error_handling)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"ERROR: Lỗi không xác định khi chạy kiểm tra: {e}")
            results.append(False)
    
    # Tổng kết
    print("\n=== KẾT QUẢ KIỂM TRA ===")
    for i, (name, _) in enumerate(tests):
        status = "PASS" if results[i] else "FAIL"
        print(f"{name}: {status}")
    
    if all(results):
        print("\nTất cả các kiểm tra đều PASS!")
    else:
        print("\nMột số kiểm tra FAIL. Vui lòng kiểm tra lại cấu hình.")

if __name__ == "__main__":
    run_all_tests()
