#!/usr/bin/env python
"""
Script chính để kiểm tra kết nối và bảo mật của Supabase
"""
import os
import sys
import argparse
from pathlib import Path

# Thêm thư mục gốc của dự án vào sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables directly.")

def print_header(title):
    """In tiêu đề với định dạng đẹp"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def main():
    """Hàm chính để chạy các kiểm tra"""
    parser = argparse.ArgumentParser(description='Kiểm tra kết nối và bảo mật của Supabase')
    parser.add_argument('--connection', action='store_true', help='Chỉ chạy kiểm tra kết nối')
    parser.add_argument('--security', action='store_true', help='Chỉ chạy kiểm tra bảo mật')
    parser.add_argument('--performance', action='store_true', help='Chỉ chạy kiểm tra hiệu suất')
    parser.add_argument('--all', action='store_true', help='Chạy tất cả các kiểm tra')
    
    args = parser.parse_args()
    
    # Nếu không có tham số nào được chỉ định, chạy tất cả các kiểm tra
    if not (args.connection or args.security or args.performance or args.all):
        args.all = True
    
    # Kiểm tra kết nối
    if args.connection or args.all:
        print_header("KIỂM TRA KẾT NỐI SUPABASE")
        from utils.supabase_test import run_all_tests
        run_all_tests()
    
    # Kiểm tra bảo mật
    if args.security or args.all:
        print_header("KIỂM TRA BẢO MẬT SUPABASE")
        from utils.security_check import run_security_checks
        run_security_checks()
    
    # Kiểm tra hiệu suất
    if args.performance or args.all:
        print_header("KIỂM TRA HIỆU SUẤT SUPABASE")
        from utils.performance_test import run_performance_tests
        run_performance_tests()
    
    print_header("KẾT THÚC KIỂM TRA")
    print("Đã hoàn thành tất cả các kiểm tra. Vui lòng xem kết quả ở trên.")

if __name__ == "__main__":
    main()
