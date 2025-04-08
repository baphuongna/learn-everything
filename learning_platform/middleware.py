"""
Middleware bảo mật tùy chỉnh cho ứng dụng
"""

class SecurityHeadersMiddleware:
    """
    Middleware thêm các header bảo mật vào HTTP response
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Content Security Policy (CSP)
        # Chỉ cho phép tài nguyên từ cùng nguồn và một số nguồn đáng tin cậy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: blob:; "
            "connect-src 'self'; "
            "frame-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self';"
        )
        
        # Ngăn chặn clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Ngăn chặn MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Bảo vệ chống XSS
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Chỉ định chính sách tham chiếu
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature Policy - giới hạn các tính năng trình duyệt
        response['Feature-Policy'] = (
            "camera 'none'; "
            "microphone 'none'; "
            "geolocation 'none'; "
            "payment 'none'"
        )
        
        # Permissions Policy (thay thế Feature Policy trong tương lai)
        response['Permissions-Policy'] = (
            "camera=(), "
            "microphone=(), "
            "geolocation=(), "
            "payment=()"
        )
        
        return response
