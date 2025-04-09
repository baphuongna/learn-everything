"""
Dịch vụ trợ lý AI.
"""
import os
import json
import logging
import requests
from django.conf import settings
from .models import AIAssistantChat, AIAssistantMessage, AIAssistantPrompt

logger = logging.getLogger(__name__)

# Cấu hình API
OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', os.environ.get('OPENAI_API_KEY', ''))
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = getattr(settings, 'OPENAI_MODEL', "gpt-3.5-turbo")
OPENAI_MAX_TOKENS = getattr(settings, 'OPENAI_MAX_TOKENS', 1000)
OPENAI_TEMPERATURE = getattr(settings, 'OPENAI_TEMPERATURE', 0.7)

def get_system_prompt(subject=None, topic=None, lesson=None):
    """
    Lấy system prompt dựa trên nội dung học tập.
    
    Args:
        subject: Đối tượng Subject (tùy chọn)
        topic: Đối tượng Topic (tùy chọn)
        lesson: Đối tượng Lesson (tùy chọn)
        
    Returns:
        str: System prompt
    """
    try:
        # Tìm prompt phù hợp nhất dựa trên nội dung học tập
        prompt = None
        
        # Nếu có bài học cụ thể
        if lesson:
            prompt = AIAssistantPrompt.objects.filter(
                prompt_type='lesson',
                lesson=lesson,
                is_active=True
            ).first()
        
        # Nếu không có prompt cho bài học, tìm prompt cho chủ đề con
        if not prompt and topic:
            prompt = AIAssistantPrompt.objects.filter(
                prompt_type='topic',
                topic=topic,
                is_active=True
            ).first()
        
        # Nếu không có prompt cho chủ đề con, tìm prompt cho chủ đề
        if not prompt and subject:
            prompt = AIAssistantPrompt.objects.filter(
                prompt_type='subject',
                subject=subject,
                is_active=True
            ).first()
        
        # Nếu không có prompt cụ thể, sử dụng prompt hệ thống mặc định
        if not prompt:
            prompt = AIAssistantPrompt.objects.filter(
                prompt_type='system',
                is_active=True
            ).first()
        
        # Nếu vẫn không có prompt, sử dụng prompt mặc định
        if prompt:
            return prompt.content
        else:
            return """Bạn là trợ lý học tập AI, giúp người dùng trả lời các câu hỏi liên quan đến nội dung học tập.
Hãy cung cấp câu trả lời ngắn gọn, chính xác và dễ hiểu.
Nếu bạn không biết câu trả lời, hãy thành thật và đề xuất cách người dùng có thể tìm thêm thông tin."""
    
    except Exception as e:
        logger.error(f"Lỗi khi lấy system prompt: {e}")
        return """Bạn là trợ lý học tập AI, giúp người dùng trả lời các câu hỏi liên quan đến nội dung học tập.
Hãy cung cấp câu trả lời ngắn gọn, chính xác và dễ hiểu.
Nếu bạn không biết câu trả lời, hãy thành thật và đề xuất cách người dùng có thể tìm thêm thông tin."""

def get_context_from_lesson(lesson):
    """
    Lấy nội dung bài học để cung cấp ngữ cảnh cho trợ lý AI.
    
    Args:
        lesson: Đối tượng Lesson
        
    Returns:
        str: Nội dung bài học
    """
    try:
        if lesson:
            return f"""Nội dung bài học "{lesson.title}":
{lesson.content}

Hãy sử dụng thông tin trên để trả lời câu hỏi của người dùng."""
        return ""
    except Exception as e:
        logger.error(f"Lỗi khi lấy nội dung bài học: {e}")
        return ""

def prepare_messages_for_api(chat, include_context=True):
    """
    Chuẩn bị danh sách tin nhắn cho API OpenAI.
    
    Args:
        chat: Đối tượng AIAssistantChat
        include_context: Có bao gồm ngữ cảnh từ bài học không
        
    Returns:
        list: Danh sách tin nhắn cho API
    """
    try:
        messages = []
        
        # Thêm system prompt
        system_prompt = get_system_prompt(chat.subject, chat.topic, chat.lesson)
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Thêm ngữ cảnh từ bài học nếu có
        if include_context and chat.lesson:
            context = get_context_from_lesson(chat.lesson)
            if context:
                messages.append({
                    "role": "system",
                    "content": context
                })
        
        # Thêm các tin nhắn từ cuộc trò chuyện
        chat_messages = chat.messages.all()
        for msg in chat_messages:
            if msg.role != 'system':  # Bỏ qua tin nhắn hệ thống
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        return messages
    
    except Exception as e:
        logger.error(f"Lỗi khi chuẩn bị tin nhắn cho API: {e}")
        return []

def call_openai_api(messages):
    """
    Gọi API OpenAI để lấy phản hồi.
    
    Args:
        messages: Danh sách tin nhắn
        
    Returns:
        str: Phản hồi từ API
    """
    try:
        if not OPENAI_API_KEY:
            logger.error("Thiếu OpenAI API key")
            return "Xin lỗi, tôi không thể trả lời ngay bây giờ do thiếu cấu hình API. Vui lòng liên hệ quản trị viên."
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        data = {
            "model": OPENAI_MODEL,
            "messages": messages,
            "max_tokens": OPENAI_MAX_TOKENS,
            "temperature": OPENAI_TEMPERATURE
        }
        
        response = requests.post(OPENAI_API_URL, headers=headers, json=data)
        
        if response.status_code == 200:
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
        else:
            logger.error(f"Lỗi API OpenAI: {response.status_code} - {response.text}")
            return f"Xin lỗi, đã xảy ra lỗi khi gọi API. Mã lỗi: {response.status_code}"
    
    except Exception as e:
        logger.error(f"Lỗi khi gọi API OpenAI: {e}")
        return "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại sau."

def get_ai_response(chat, user_message):
    """
    Lấy phản hồi từ trợ lý AI cho tin nhắn của người dùng.
    
    Args:
        chat: Đối tượng AIAssistantChat
        user_message: Nội dung tin nhắn của người dùng
        
    Returns:
        str: Phản hồi từ trợ lý AI
    """
    try:
        # Lưu tin nhắn của người dùng
        AIAssistantMessage.objects.create(
            chat=chat,
            role='user',
            content=user_message
        )
        
        # Chuẩn bị tin nhắn cho API
        messages = prepare_messages_for_api(chat)
        
        # Gọi API OpenAI
        ai_response = call_openai_api(messages)
        
        # Lưu phản hồi của trợ lý AI
        AIAssistantMessage.objects.create(
            chat=chat,
            role='assistant',
            content=ai_response
        )
        
        return ai_response
    
    except Exception as e:
        logger.error(f"Lỗi khi lấy phản hồi từ trợ lý AI: {e}")
        error_message = "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại sau."
        
        # Lưu tin nhắn lỗi
        AIAssistantMessage.objects.create(
            chat=chat,
            role='assistant',
            content=error_message
        )
        
        return error_message

def create_new_chat(user, subject=None, topic=None, lesson=None, title=None):
    """
    Tạo cuộc trò chuyện mới với trợ lý AI.
    
    Args:
        user: Đối tượng User
        subject: Đối tượng Subject (tùy chọn)
        topic: Đối tượng Topic (tùy chọn)
        lesson: Đối tượng Lesson (tùy chọn)
        title: Tiêu đề cuộc trò chuyện (tùy chọn)
        
    Returns:
        AIAssistantChat: Cuộc trò chuyện mới
    """
    try:
        # Tạo tiêu đề mặc định nếu không có
        if not title:
            if lesson:
                title = f"Trò chuyện về {lesson.title}"
            elif topic:
                title = f"Trò chuyện về {topic.name}"
            elif subject:
                title = f"Trò chuyện về {subject.name}"
            else:
                title = "Cuộc trò chuyện mới"
        
        # Tạo cuộc trò chuyện mới
        chat = AIAssistantChat.objects.create(
            user=user,
            title=title,
            subject=subject,
            topic=topic,
            lesson=lesson
        )
        
        # Thêm tin nhắn hệ thống
        system_prompt = get_system_prompt(subject, topic, lesson)
        AIAssistantMessage.objects.create(
            chat=chat,
            role='system',
            content=system_prompt
        )
        
        # Thêm ngữ cảnh từ bài học nếu có
        if lesson:
            context = get_context_from_lesson(lesson)
            if context:
                AIAssistantMessage.objects.create(
                    chat=chat,
                    role='system',
                    content=context
                )
        
        return chat
    
    except Exception as e:
        logger.error(f"Lỗi khi tạo cuộc trò chuyện mới: {e}")
        return None
