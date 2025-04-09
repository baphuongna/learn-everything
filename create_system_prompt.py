"""
Script tạo dữ liệu mẫu cho prompt hệ thống.
"""
import os
import django

# Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning_platform.settings')
django.setup()

# Import model
from ai_assistant.models import AIAssistantPrompt

# Tạo prompt hệ thống
system_prompt = """Bạn là trợ lý học tập AI, giúp người dùng trả lời các câu hỏi liên quan đến nội dung học tập.
Hãy cung cấp câu trả lời ngắn gọn, chính xác và dễ hiểu.
Nếu bạn không biết câu trả lời, hãy thành thật và đề xuất cách người dùng có thể tìm thêm thông tin."""

# Kiểm tra xem đã có prompt hệ thống chưa
if not AIAssistantPrompt.objects.filter(prompt_type='system').exists():
    AIAssistantPrompt.objects.create(
        name='System Prompt',
        prompt_type='system',
        content=system_prompt,
        is_active=True
    )
    print("Đã tạo prompt hệ thống thành công!")
else:
    print("Prompt hệ thống đã tồn tại!")

# Tạo prompt chung
general_prompt = """Tôi sẽ giúp bạn học tập hiệu quả bằng cách:
1. Giải thích các khái niệm phức tạp một cách đơn giản
2. Cung cấp ví dụ thực tế để minh họa
3. Gợi ý các phương pháp học tập phù hợp
4. Trả lời các câu hỏi về nội dung bài học
5. Giúp bạn ôn tập và củng cố kiến thức

Hãy đặt câu hỏi về bất kỳ chủ đề nào bạn đang học!"""

# Kiểm tra xem đã có prompt chung chưa
if not AIAssistantPrompt.objects.filter(prompt_type='general').exists():
    AIAssistantPrompt.objects.create(
        name='General Prompt',
        prompt_type='general',
        content=general_prompt,
        is_active=True
    )
    print("Đã tạo prompt chung thành công!")
else:
    print("Prompt chung đã tồn tại!")
