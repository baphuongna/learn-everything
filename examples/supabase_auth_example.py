"""
Ví dụ về cách sử dụng Supabase Auth trong Django
"""
from utils.supabase_client import supabase

def sign_up(email, password, metadata=None):
    """
    Đăng ký người dùng mới với Supabase Auth
    
    Args:
        email (str): Email của người dùng
        password (str): Mật khẩu của người dùng
        metadata (dict, optional): Metadata bổ sung cho người dùng
        
    Returns:
        dict: Kết quả đăng ký
    """
    try:
        auth_data = {
            "email": email,
            "password": password,
        }
        
        if metadata:
            auth_data["options"] = {
                "data": metadata
            }
            
        response = supabase.client.auth.sign_up(auth_data)
        return response
    except Exception as e:
        print(f"Lỗi khi đăng ký: {e}")
        return None

def sign_in(email, password):
    """
    Đăng nhập với Supabase Auth
    
    Args:
        email (str): Email của người dùng
        password (str): Mật khẩu của người dùng
        
    Returns:
        dict: Kết quả đăng nhập
    """
    try:
        response = supabase.client.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        return response
    except Exception as e:
        print(f"Lỗi khi đăng nhập: {e}")
        return None

def sign_out(session_token=None):
    """
    Đăng xuất khỏi Supabase Auth
    
    Args:
        session_token (str, optional): Token phiên làm việc
        
    Returns:
        dict: Kết quả đăng xuất
    """
    try:
        if session_token:
            supabase.client.auth.set_session(session_token)
        response = supabase.client.auth.sign_out()
        return response
    except Exception as e:
        print(f"Lỗi khi đăng xuất: {e}")
        return None

def reset_password(email):
    """
    Gửi email đặt lại mật khẩu
    
    Args:
        email (str): Email của người dùng
        
    Returns:
        dict: Kết quả gửi email
    """
    try:
        response = supabase.client.auth.reset_password_for_email(email)
        return response
    except Exception as e:
        print(f"Lỗi khi gửi email đặt lại mật khẩu: {e}")
        return None

def update_user(user_data):
    """
    Cập nhật thông tin người dùng
    
    Args:
        user_data (dict): Dữ liệu người dùng cần cập nhật
        
    Returns:
        dict: Kết quả cập nhật
    """
    try:
        response = supabase.client.auth.update_user(user_data)
        return response
    except Exception as e:
        print(f"Lỗi khi cập nhật thông tin người dùng: {e}")
        return None

def get_user(session_token=None):
    """
    Lấy thông tin người dùng hiện tại
    
    Args:
        session_token (str, optional): Token phiên làm việc
        
    Returns:
        dict: Thông tin người dùng
    """
    try:
        if session_token:
            supabase.client.auth.set_session(session_token)
        response = supabase.client.auth.get_user()
        return response
    except Exception as e:
        print(f"Lỗi khi lấy thông tin người dùng: {e}")
        return None

def refresh_session(refresh_token):
    """
    Làm mới phiên làm việc
    
    Args:
        refresh_token (str): Token làm mới
        
    Returns:
        dict: Kết quả làm mới phiên
    """
    try:
        response = supabase.client.auth.refresh_session(refresh_token)
        return response
    except Exception as e:
        print(f"Lỗi khi làm mới phiên: {e}")
        return None

def sign_in_with_provider(provider):
    """
    Đăng nhập với nhà cung cấp bên thứ ba
    
    Args:
        provider (str): Tên nhà cung cấp (google, facebook, github, v.v.)
        
    Returns:
        dict: URL đăng nhập
    """
    try:
        response = supabase.client.auth.sign_in_with_oauth({
            "provider": provider
        })
        return response
    except Exception as e:
        print(f"Lỗi khi đăng nhập với {provider}: {e}")
        return None

# Ví dụ về cách sử dụng trong Django view
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .forms import SignUpForm, SignInForm
from examples.supabase_auth_example import sign_up, sign_in, sign_out, get_user

def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Metadata bổ sung
            metadata = {
                'full_name': form.cleaned_data['full_name'],
                'role': 'user'
            }
            
            # Đăng ký với Supabase
            response = sign_up(email, password, metadata)
            
            if response and response.user:
                messages.success(request, 'Đăng ký thành công! Vui lòng kiểm tra email để xác nhận tài khoản.')
                return redirect('login')
            else:
                messages.error(request, 'Có lỗi xảy ra khi đăng ký.')
    else:
        form = SignUpForm()
    
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Đăng nhập với Supabase
            response = sign_in(email, password)
            
            if response and response.user:
                # Lưu token vào session
                request.session['access_token'] = response.session.access_token
                request.session['refresh_token'] = response.session.refresh_token
                
                messages.success(request, 'Đăng nhập thành công!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Email hoặc mật khẩu không đúng.')
    else:
        form = SignInForm()
    
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    # Lấy token từ session
    access_token = request.session.get('access_token')
    
    # Đăng xuất với Supabase
    sign_out(access_token)
    
    # Xóa token khỏi session
    if 'access_token' in request.session:
        del request.session['access_token']
    if 'refresh_token' in request.session:
        del request.session['refresh_token']
    
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('login')

def profile_view(request):
    # Lấy token từ session
    access_token = request.session.get('access_token')
    
    if not access_token:
        messages.error(request, 'Vui lòng đăng nhập để xem trang này.')
        return redirect('login')
    
    # Lấy thông tin người dùng
    response = get_user(access_token)
    
    if response and response.user:
        user_data = response.user
        return render(request, 'auth/profile.html', {'user': user_data})
    else:
        messages.error(request, 'Không thể lấy thông tin người dùng.')
        return redirect('login')
"""
