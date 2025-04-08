#!/usr/bin/env python
"""
Script đơn giản để kiểm tra kết nối với Supabase
"""
import os
import sys
from pathlib import Path
import time

# Thêm thư mục gốc của dự án vào sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Đã tải biến môi trường từ file .env")
except ImportError:
    print("WARNING: python-dotenv không được cài đặt. Sử dụng biến môi trường trực tiếp.")

def test_supabase_api():
    """Kiểm tra kết nối đến Supabase API"""
    try:
        from utils.supabase_client import supabase
        
        print("\n=== KIỂM TRA KẾT NỐI SUPABASE API ===")
        
        # Lấy thông tin kết nối
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        print(f"URL: {supabase_url}")
        print(f"Key: {supabase_key[:10]}...{supabase_key[-5:]}")
        
        # Đo thời gian kết nối
        start_time = time.time()
        
        # Thử lấy dữ liệu từ bảng hệ thống
        response = supabase.client.from_("_schema.tables").select("*").limit(1).execute()
        
        end_time = time.time()
        latency = (end_time - start_time) * 1000  # Chuyển đổi sang milliseconds
        
        if response.data:
            print(f"✓ Kết nối đến Supabase API thành công ({latency:.2f}ms)")
            print(f"✓ Dữ liệu nhận được: {response.data}")
            return True
        else:
            print(f"✓ Kết nối đến Supabase API thành công ({latency:.2f}ms)")
            print("WARNING: Không có dữ liệu trả về")
            return True
    except Exception as e:
        print(f"ERROR: Không thể kết nối đến Supabase API: {e}")
        return False

def test_postgres_connection():
    """Kiểm tra kết nối đến Supabase PostgreSQL"""
    try:
        import psycopg2
        
        print("\n=== KIỂM TRA KẾT NỐI SUPABASE POSTGRESQL ===")
        
        # Lấy thông tin kết nối từ biến môi trường
        db_host = os.environ.get('SUPABASE_DB_HOST')
        db_port = os.environ.get('SUPABASE_DB_PORT')
        db_name = os.environ.get('SUPABASE_DB_NAME')
        db_user = os.environ.get('SUPABASE_DB_USER')
        db_password = os.environ.get('SUPABASE_DB_PASSWORD')
        
        print(f"Host: {db_host}")
        print(f"Port: {db_port}")
        print(f"Database: {db_name}")
        print(f"User: {db_user}")
        print(f"Password: {'*' * len(db_password) if db_password else 'Not set'}")
        
        # Tạo connection string
        conn_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode=require"
        print(f"Connection string: postgresql://{db_user}:******@{db_host}:{db_port}/{db_name}?sslmode=require")
        
        # Đo thời gian kết nối
        start_time = time.time()
        
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
        
        end_time = time.time()
        latency = (end_time - start_time) * 1000  # Chuyển đổi sang milliseconds
        
        # Đóng kết nối
        cursor.close()
        conn.close()
        
        print(f"✓ Kết nối đến Supabase PostgreSQL thành công ({latency:.2f}ms)")
        print(f"✓ Phiên bản PostgreSQL: {version[0]}")
        return True
    except ImportError:
        print("ERROR: Không thể import psycopg2. Vui lòng cài đặt: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"ERROR: Không thể kết nối đến Supabase PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    print("=== KIỂM TRA KẾT NỐI SUPABASE ===\n")
    
    api_result = test_supabase_api()
    db_result = test_postgres_connection()
    
    print("\n=== KẾT QUẢ KIỂM TRA ===")
    print(f"Kết nối Supabase API: {'PASS' if api_result else 'FAIL'}")
    print(f"Kết nối PostgreSQL: {'PASS' if db_result else 'FAIL'}")
    
    if api_result and db_result:
        print("\n✓ Tất cả các kiểm tra đều PASS! Kết nối Supabase hoạt động tốt.")
    else:
        print("\nMột số kiểm tra FAIL. Vui lòng kiểm tra lại cấu hình.")
