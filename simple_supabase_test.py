#!/usr/bin/env python
"""
Script đơn giản để kiểm tra kết nối với Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Lấy thông tin kết nối từ biến môi trường
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

print(f"URL: {supabase_url}")
print(f"Key: {supabase_key[:10]}...{supabase_key[-5:]}")

# Tạo Supabase client
supabase = create_client(supabase_url, supabase_key)

# Kiểm tra kết nối Supabase API
try:
    print("\nKiểm tra kết nối Supabase API...")

    # Thử truy vấn bảng công khai
    try:
        print("Thử truy vấn bảng...")
        # Thử với một số bảng công khai phổ biến
        for table_name in ['users', 'profiles', 'todos']:
            try:
                print(f"Thử truy vấn bảng '{table_name}'...")
                response = supabase.from_(table_name).select("*").limit(1).execute()
                print(f"Truy vấn bảng '{table_name}' thành công!")
                print(f"Dữ liệu: {response.data}")
                break
            except Exception as table_error:
                print(f"Không thể truy vấn bảng '{table_name}': {table_error}")
    except Exception as e:
        print(f"Lỗi khi truy vấn bảng: {e}")

    # Thử sử dụng Storage API
    try:
        print("\nThử sử dụng Storage API...")
        buckets = supabase.storage.list_buckets()
        print(f"Danh sách buckets: {buckets}")
    except Exception as e:
        print(f"Lỗi khi sử dụng Storage API: {e}")

except Exception as e:
    print(f"Lỗi kết nối Supabase API: {e}")

# Kiểm tra kết nối PostgreSQL
try:
    import psycopg2

    # Lấy thông tin kết nối từ biến môi trường
    db_host = os.environ.get('SUPABASE_DB_HOST')
    db_port = os.environ.get('SUPABASE_DB_PORT')
    db_name = os.environ.get('SUPABASE_DB_NAME')
    db_user = os.environ.get('SUPABASE_DB_USER')
    db_password = os.environ.get('SUPABASE_DB_PASSWORD')

    print(f"\nThông tin kết nối PostgreSQL:")
    print(f"Host: {db_host}")
    print(f"Port: {db_port}")
    print(f"Database: {db_name}")
    print(f"User: {db_user}")
    print(f"Password: {'*' * len(db_password) if db_password else 'Not set'}")

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

    print(f"Kết nối PostgreSQL thành công!")
    print(f"Phiên bản PostgreSQL: {version[0]}")
except Exception as e:
    print(f"Lỗi kết nối PostgreSQL: {e}")
