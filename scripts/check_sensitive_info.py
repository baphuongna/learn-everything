#!/usr/bin/env python
"""
Script kiểm tra thông tin nhạy cảm trong mã nguồn trước khi commit
"""
import os
import re
import sys
from pathlib import Path

# Thư mục gốc của dự án
BASE_DIR = Path(__file__).resolve().parent.parent

# Các mẫu regex để tìm thông tin nhạy cảm
SENSITIVE_PATTERNS = [
    # API keys, tokens, credentials
    r'api[_-]?key[_-]?(?:id)?[\s:=]+[\'"`]([^\s\'"`]{8,})[\'"`]',
    r'(?:access|auth|jwt|session|secret)[_-]?(?:key|token|secret)[\s:=]+[\'"`]([^\s\'"`]{8,})[\'"`]',
    r'(?:password|passwd|pwd)[\s:=]+[\'"`]([^\s\'"`]{3,})[\'"`]',
    
    # Database connection strings
    r'(?:jdbc|odbc|mongodb|redis|postgres|mysql|sqlite|oracle):([^\s\'"`]+)',
    r'(?:connection|conn)[_-]?(?:string|str|url)[\s:=]+[\'"`]([^\s\'"`]+)[\'"`]',
    
    # AWS specific
    r'(?:aws)[_-]?(?:access|secret)[_-]?key[_-]?(?:id)?[\s:=]+[\'"`]([^\s\'"`]{16,})[\'"`]',
    
    # Private keys and certificates
    r'-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----',
    r'-----BEGIN CERTIFICATE-----',
]

# Các file và thư mục cần bỏ qua
IGNORE_DIRS = [
    '.git',
    'venv',
    'env',
    'node_modules',
    '__pycache__',
    'migrations',
    'static',
    'media',
]

IGNORE_FILES = [
    '.gitignore',
    '.env.example',
    'check_sensitive_info.py',  # Bỏ qua chính script này
]

IGNORE_EXTENSIONS = [
    '.pyc',
    '.pyo',
    '.so',
    '.o',
    '.a',
    '.dll',
    '.exe',
    '.bin',
    '.png',
    '.jpg',
    '.jpeg',
    '.gif',
    '.svg',
    '.ico',
    '.pdf',
    '.zip',
    '.tar',
    '.gz',
    '.rar',
]

def should_ignore(path):
    """Kiểm tra xem có nên bỏ qua file/thư mục này không"""
    path_parts = path.parts
    
    # Kiểm tra thư mục cần bỏ qua
    for part in path_parts:
        if part in IGNORE_DIRS:
            return True
    
    # Kiểm tra file cần bỏ qua
    if path.name in IGNORE_FILES:
        return True
    
    # Kiểm tra phần mở rộng cần bỏ qua
    if path.suffix in IGNORE_EXTENSIONS:
        return True
    
    return False

def check_file(file_path):
    """Kiểm tra một file có chứa thông tin nhạy cảm không"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Bỏ qua các file nhị phân
        return []
    except Exception as e:
        print(f"Lỗi khi đọc file {file_path}: {e}")
        return []
    
    findings = []
    
    for i, line in enumerate(content.splitlines(), 1):
        for pattern in SENSITIVE_PATTERNS:
            matches = re.finditer(pattern, line)
            for match in matches:
                # Bỏ qua các trường hợp giả dương phổ biến
                if any(fp in line.lower() for fp in [
                    'example', 
                    'placeholder', 
                    'sample', 
                    'your-', 
                    'xxx', 
                    'test', 
                    'dummy',
                    'template',
                ]):
                    continue
                
                findings.append({
                    'file': str(file_path),
                    'line': i,
                    'pattern': pattern,
                    'content': line.strip(),
                })
    
    return findings

def scan_directory(directory=BASE_DIR):
    """Quét toàn bộ thư mục để tìm thông tin nhạy cảm"""
    all_findings = []
    
    for path in Path(directory).rglob('*'):
        if path.is_file() and not should_ignore(path):
            findings = check_file(path)
            all_findings.extend(findings)
    
    return all_findings

def main():
    """Hàm chính"""
    print("Đang kiểm tra thông tin nhạy cảm trong mã nguồn...")
    
    findings = scan_directory()
    
    if findings:
        print(f"\n⚠️ Tìm thấy {len(findings)} thông tin nhạy cảm tiềm ẩn:")
        
        for i, finding in enumerate(findings, 1):
            print(f"\n{i}. File: {finding['file']}")
            print(f"   Dòng: {finding['line']}")
            print(f"   Nội dung: {finding['content']}")
        
        print("\n❌ Kiểm tra thất bại! Vui lòng xử lý các thông tin nhạy cảm trước khi commit.")
        print("   Gợi ý: Di chuyển thông tin nhạy cảm vào file .env và sử dụng biến môi trường.")
        sys.exit(1)
    else:
        print("\n✅ Không tìm thấy thông tin nhạy cảm trong mã nguồn.")
        sys.exit(0)

if __name__ == "__main__":
    main()
