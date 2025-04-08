"""
Ví dụ về cách sử dụng Supabase trong Django
"""
from utils.supabase_client import supabase

def get_all_users():
    """
    Lấy danh sách tất cả người dùng từ Supabase
    """
    try:
        response = supabase.get_data('users')
        return response.data
    except Exception as e:
        print(f"Lỗi khi lấy danh sách người dùng: {e}")
        return []

def get_user_by_id(user_id):
    """
    Lấy thông tin người dùng theo ID
    """
    try:
        query_params = {
            'filter': [('id', 'eq', user_id)]
        }
        response = supabase.get_data('users', query_params)
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Lỗi khi lấy thông tin người dùng: {e}")
        return None

def create_user(user_data):
    """
    Tạo người dùng mới trong Supabase
    """
    try:
        response = supabase.insert_data('users', user_data)
        return response.data
    except Exception as e:
        print(f"Lỗi khi tạo người dùng: {e}")
        return None

def update_user(user_id, user_data):
    """
    Cập nhật thông tin người dùng
    """
    try:
        response = supabase.update_data('users', user_data, 'id', user_id)
        return response.data
    except Exception as e:
        print(f"Lỗi khi cập nhật người dùng: {e}")
        return None

def delete_user(user_id):
    """
    Xóa người dùng
    """
    try:
        response = supabase.delete_data('users', 'id', user_id)
        return response.data
    except Exception as e:
        print(f"Lỗi khi xóa người dùng: {e}")
        return None

# Ví dụ về cách sử dụng trong Django view
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserForm
from examples.supabase_example import get_all_users, create_user

def user_list(request):
    users = get_all_users()
    return render(request, 'users/list.html', {'users': users})

def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user_data = {
                'name': form.cleaned_data['name'],
                'email': form.cleaned_data['email'],
                'role': form.cleaned_data['role'],
            }
            result = create_user(user_data)
            if result:
                messages.success(request, 'Người dùng đã được tạo thành công!')
                return redirect('user_list')
            else:
                messages.error(request, 'Có lỗi xảy ra khi tạo người dùng.')
    else:
        form = UserForm()
    
    return render(request, 'users/create.html', {'form': form})
"""
