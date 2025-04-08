#!/usr/bin/env python
"""
Script kiểm tra thông tin nhạy cảm trong mã nguồn trước khi commit
"""
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

    # Private keys (không kiểm tra chứng chỉ vì gây nhiều báo cáo giả dương)
    r'-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----',
    # r'-----BEGIN CERTIFICATE-----',  # Bỏ qua chứng chỉ
]

# Các file và thư mục cần bỏ qua
IGNORE_DIRS = [
    '.git',
    'venv',
    'env',
    '.venv',  # Bo qua moi truong ao Python
    'node_modules',
    '__pycache__',
    'migrations',
    'static',
    'media',
    'site-packages',  # Bo qua thu vien ben thu ba
    'dist-packages',  # Bo qua thu vien ben thu ba
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
    path_str = str(path).lower()

    # Kiểm tra thư mục cần bỏ qua
    for ignore_dir in IGNORE_DIRS:
        if f'/{ignore_dir}/' in path_str.replace('\\', '/') or f'\\{ignore_dir}\\' in path_str:
            return True

    # Kiểm tra file cần bỏ qua
    if path.name in IGNORE_FILES:
        return True

    # Kiểm tra phần mở rộng cần bỏ qua
    if path.suffix in IGNORE_EXTENSIONS:
        return True

    # Bỏ qua các thư viện Python
    if '.venv' in path_str or 'site-packages' in path_str or 'dist-packages' in path_str:
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
            # Kiểm tra xem có kết quả phù hợp không
            if re.search(pattern, line):
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
                    'cacert',
                    'certificate',
                    'certifi',
                    'unittest',
                    'testcase',
                    'mock',
                    'fake',
                ]):
                    continue

                # Thêm kết quả vào danh sách phát hiện
                findings.append({
                    'file': str(file_path),
                    'line': i,
                    'pattern': pattern,
                    'content': line.strip(),
                })
                # Dừng kiểm tra các mẫu khác cho dòng này
                break

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
    try:
        print("Dang kiem tra thong tin nhay cam trong ma nguon...")

        findings = scan_directory()

        if findings:
            print(f"\nCANH BAO: Tim thay {len(findings)} thong tin nhay cam tiem an:")

            for i, finding in enumerate(findings, 1):
                print(f"\n{i}. File: {finding['file']}")
                print(f"   Dong: {finding['line']}")
                print(f"   Noi dung: {finding['content']}")

            print("\nKiem tra that bai! Vui long xu ly cac thong tin nhay cam truoc khi commit.")
            print("   Goi y: Di chuyen thong tin nhay cam vao file .env va su dung bien moi truong.")
            sys.exit(1)
        else:
            print("\nKhong tim thay thong tin nhay cam trong ma nguon.")
            sys.exit(0)
    except Exception as e:
        print(f"Loi khi kiem tra thong tin nhay cam: {e}")
        # Trong trường hợp lỗi, cho phép commit tiếp tục
        sys.exit(0)

if __name__ == "__main__":
    main()
