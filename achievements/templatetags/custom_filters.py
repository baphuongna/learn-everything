from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Trừ arg từ value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        try:
            return float(value) - float(arg)
        except (ValueError, TypeError):
            return 0

@register.filter
def percentage(value, total):
    """Tính phần trăm của value trên total."""
    try:
        if int(total) == 0:
            return 0
        return int((int(value) / int(total)) * 100)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def abs(value):
    """Trả về giá trị tuyệt đối của một số.
    Ví dụ: {{ value|abs }}
    """
    try:
        return abs(int(value))
    except (ValueError, TypeError):
        try:
            return abs(float(value))
        except (ValueError, TypeError):
            return value
