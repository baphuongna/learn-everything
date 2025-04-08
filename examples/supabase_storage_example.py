"""
Ví dụ về cách sử dụng Supabase Storage trong Django
"""
import os
from utils.supabase_client import supabase

def upload_file_to_supabase(bucket_name, file_path, file_content):
    """
    Tải lên file vào Supabase Storage
    
    Args:
        bucket_name (str): Tên bucket trong Supabase Storage
        file_path (str): Đường dẫn file trong bucket
        file_content (bytes): Nội dung file dạng bytes
        
    Returns:
        dict: Kết quả tải lên
    """
    try:
        response = supabase.client.storage.from_(bucket_name).upload(
            file_path,
            file_content,
            {"content-type": "application/octet-stream"}
        )
        return response
    except Exception as e:
        print(f"Lỗi khi tải lên file: {e}")
        return None

def get_public_url(bucket_name, file_path):
    """
    Lấy URL công khai của file trong Supabase Storage
    
    Args:
        bucket_name (str): Tên bucket trong Supabase Storage
        file_path (str): Đường dẫn file trong bucket
        
    Returns:
        str: URL công khai của file
    """
    try:
        url = supabase.client.storage.from_(bucket_name).get_public_url(file_path)
        return url
    except Exception as e:
        print(f"Lỗi khi lấy URL công khai: {e}")
        return None

def download_file(bucket_name, file_path, save_path):
    """
    Tải file từ Supabase Storage
    
    Args:
        bucket_name (str): Tên bucket trong Supabase Storage
        file_path (str): Đường dẫn file trong bucket
        save_path (str): Đường dẫn lưu file trên máy local
        
    Returns:
        bool: True nếu tải xuống thành công, False nếu thất bại
    """
    try:
        response = supabase.client.storage.from_(bucket_name).download(file_path)
        
        # Lưu file vào đường dẫn chỉ định
        with open(save_path, 'wb') as f:
            f.write(response)
            
        return True
    except Exception as e:
        print(f"Lỗi khi tải xuống file: {e}")
        return False

def list_files(bucket_name, folder_path=None):
    """
    Liệt kê các file trong bucket
    
    Args:
        bucket_name (str): Tên bucket trong Supabase Storage
        folder_path (str, optional): Đường dẫn thư mục trong bucket
        
    Returns:
        list: Danh sách các file
    """
    try:
        if folder_path:
            response = supabase.client.storage.from_(bucket_name).list(folder_path)
        else:
            response = supabase.client.storage.from_(bucket_name).list()
        return response
    except Exception as e:
        print(f"Lỗi khi liệt kê file: {e}")
        return []

def delete_file(bucket_name, file_path):
    """
    Xóa file từ Supabase Storage
    
    Args:
        bucket_name (str): Tên bucket trong Supabase Storage
        file_path (str): Đường dẫn file trong bucket
        
    Returns:
        dict: Kết quả xóa file
    """
    try:
        response = supabase.client.storage.from_(bucket_name).remove([file_path])
        return response
    except Exception as e:
        print(f"Lỗi khi xóa file: {e}")
        return None

def create_signed_url(bucket_name, file_path, expires_in=60):
    """
    Tạo URL có chữ ký (signed URL) cho file
    
    Args:
        bucket_name (str): Tên bucket trong Supabase Storage
        file_path (str): Đường dẫn file trong bucket
        expires_in (int, optional): Thời gian hết hạn của URL (giây)
        
    Returns:
        str: URL có chữ ký
    """
    try:
        response = supabase.client.storage.from_(bucket_name).create_signed_url(
            file_path, expires_in
        )
        return response['signedURL']
    except Exception as e:
        print(f"Lỗi khi tạo signed URL: {e}")
        return None

def move_file(bucket_name, old_path, new_path):
    """
    Di chuyển file trong Supabase Storage
    
    Args:
        bucket_name (str): Tên bucket trong Supabase Storage
        old_path (str): Đường dẫn hiện tại của file
        new_path (str): Đường dẫn mới của file
        
    Returns:
        dict: Kết quả di chuyển file
    """
    try:
        response = supabase.client.storage.from_(bucket_name).move(old_path, new_path)
        return response
    except Exception as e:
        print(f"Lỗi khi di chuyển file: {e}")
        return None

# Ví dụ về cách sử dụng trong Django view
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
import os
from .forms import FileUploadForm
from examples.supabase_storage_example import upload_file_to_supabase, get_public_url

def upload_file_view(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            
            # Đọc nội dung file
            file_content = uploaded_file.read()
            
            # Tạo đường dẫn file trong Supabase Storage
            file_path = f"uploads/{request.user.id}/{uploaded_file.name}"
            
            # Tải lên file vào Supabase Storage
            result = upload_file_to_supabase('public', file_path, file_content)
            
            if result:
                # Lấy URL công khai của file
                file_url = get_public_url('public', file_path)
                
                # Lưu thông tin file vào cơ sở dữ liệu
                file_record = form.save(commit=False)
                file_record.user = request.user
                file_record.file_path = file_path
                file_record.file_url = file_url
                file_record.save()
                
                messages.success(request, 'File đã được tải lên thành công!')
                return redirect('file_list')
            else:
                messages.error(request, 'Có lỗi xảy ra khi tải lên file.')
    else:
        form = FileUploadForm()
    
    return render(request, 'files/upload.html', {'form': form})
"""
