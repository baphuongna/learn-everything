#!/usr/bin/env python
"""
Script tự động tạo file .env từ file .env.example
"""
import os
import secrets
from pathlib import Path

def generate_secret_key():
    """Tạo SECRET_KEY ngẫu nhiên"""
    return secrets.token_hex(32)

def main():
    """Hàm chính"""
    # Đường dẫn đến thư mục gốc của dự án
    base_dir = Path(__file__).resolve().parent.parent
    
    # Đường dẫn đến file .env.example và .env
    env_example_path = base_dir / '.env.example'
    env_path = base_dir / '.env'
    
    # Kiểm tra xem file .env.example có tồn tại không
    if not env_example_path.exists():
        print(f"Lỗi: Không tìm thấy file {env_example_path}")
        return
    
    # Kiểm tra xem file .env đã tồn tại chưa
    if env_path.exists():
        overwrite = input(f"File {env_path} đã tồn tại. Bạn có muốn ghi đè không? (y/n): ")
        if overwrite.lower() != 'y':
            print("Hủy thiết lập.")
            return
    
    # Đọc nội dung file .env.example
    with open(env_example_path, 'r', encoding='utf-8') as f:
        env_example_content = f.read()
    
    # Tạo nội dung cho file .env
    env_content = env_example_content
    
    # Thay thế các giá trị mẫu bằng giá trị thực tế
    replacements = {
        'your-secret-key-here': generate_secret_key(),
        'your-supabase-anon-key': input("Nhập Supabase Anon Key: "),
        'your-supabase-service-role-key': input("Nhập Supabase Service Role Key: "),
        'your-project-id': input("Nhập Supabase Project ID: "),
        'your-database-password': input("Nhập mật khẩu cơ sở dữ liệu: "),
        'aws-0-region-code': input("Nhập region code của Supabase Pooler (ví dụ: ap-southeast-1): "),
        'yourdomain.com': input("Nhập domain của bạn (để trống nếu chỉ sử dụng localhost): ") or 'yourdomain.com',
    }
    
    for placeholder, value in replacements.items():
        env_content = env_content.replace(placeholder, value)
    
    # Ghi nội dung vào file .env
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"\n✅ Đã tạo file {env_path} thành công!")
    print("⚠️ Lưu ý: File này chứa thông tin nhạy cảm. Không commit lên Git.")

if __name__ == "__main__":
    main()
