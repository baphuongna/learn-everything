import uuid
from datetime import datetime, timedelta
from icalendar import Calendar, Event, Alarm
from django.utils import timezone
from django.conf import settings

def generate_ical_for_goal(goal):
    """
    Tạo file iCalendar cho mục tiêu học tập
    
    Args:
        goal: Đối tượng LearningGoal
    
    Returns:
        Chuỗi iCalendar
    """
    # Tạo calendar
    cal = Calendar()
    cal.add('prodid', '-//Learning Platform//learningplatform.com//')
    cal.add('version', '2.0')
    
    # Tạo event
    event = Event()
    event.add('summary', goal.title)
    event.add('description', goal.description or f'Mục tiêu học tập: {goal.title}')
    
    # Thêm thời gian bắt đầu và kết thúc
    start_date = goal.start_date
    end_date = goal.end_date + timedelta(days=1)  # Kết thúc vào cuối ngày
    
    event.add('dtstart', start_date)
    event.add('dtend', end_date)
    
    # Thêm thông tin khác
    event.add('dtstamp', timezone.now())
    event.add('created', goal.created_at)
    event.add('last-modified', goal.updated_at)
    event.add('uid', str(uuid.uuid4()))
    
    # Thêm thông tin về tiến độ
    event.add('x-progress', str(goal.progress_percentage))
    event.add('x-target', str(goal.target_value))
    event.add('x-current', str(goal.current_value))
    
    # Thêm nhắc nhở
    if goal.reminder_enabled:
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', f'Nhắc nhở: {goal.title}')
        
        # Nhắc nhở trước 1 ngày
        alarm.add('trigger', timedelta(days=-1))
        event.add_component(alarm)
    
    # Thêm event vào calendar
    cal.add_component(event)
    
    return cal.to_ical()

def generate_google_calendar_link(goal):
    """
    Tạo link Google Calendar cho mục tiêu học tập
    
    Args:
        goal: Đối tượng LearningGoal
    
    Returns:
        Link Google Calendar
    """
    base_url = 'https://calendar.google.com/calendar/render'
    
    # Định dạng ngày thành ISO
    start_date = goal.start_date.strftime('%Y%m%d')
    end_date = (goal.end_date + timedelta(days=1)).strftime('%Y%m%d')  # Kết thúc vào cuối ngày
    
    # Tạo tham số
    params = {
        'action': 'TEMPLATE',
        'text': goal.title,
        'details': goal.description or f'Mục tiêu học tập: {goal.title}\n\nTiến độ: {goal.progress_percentage}%\nGiá trị hiện tại: {goal.current_value}/{goal.target_value}',
        'dates': f'{start_date}/{end_date}',
        'sf': 'true',
        'output': 'xml'
    }
    
    # Tạo URL
    url = f'{base_url}?'
    for key, value in params.items():
        url += f'{key}={value}&'
    
    return url[:-1]  # Bỏ dấu & cuối cùng
