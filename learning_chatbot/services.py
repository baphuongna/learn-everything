"""
Dịch vụ chatbot hỗ trợ học tập.
"""
import re
import uuid
import logging
import difflib
from django.db.models import Q
from .models import ChatbotCategory, ChatbotQuestion, ChatbotConversation, ChatbotMessage

logger = logging.getLogger(__name__)

def create_conversation(user):
    """
    Tạo cuộc trò chuyện mới với chatbot.
    
    Args:
        user: Đối tượng User
        
    Returns:
        ChatbotConversation: Cuộc trò chuyện mới
    """
    try:
        # Tạo session ID ngẫu nhiên
        session_id = str(uuid.uuid4())
        
        # Tạo cuộc trò chuyện mới
        conversation = ChatbotConversation.objects.create(
            user=user,
            session_id=session_id,
            is_active=True
        )
        
        # Thêm tin nhắn chào mừng
        welcome_message = "Xin chào! Tôi là chatbot hỗ trợ học tập. Tôi có thể giúp gì cho bạn hôm nay?"
        ChatbotMessage.objects.create(
            conversation=conversation,
            role='bot',
            content=welcome_message
        )
        
        return conversation
    
    except Exception as e:
        logger.error(f"Lỗi khi tạo cuộc trò chuyện mới: {e}")
        return None

def find_matching_question(user_message, subject=None, topic=None, lesson=None):
    """
    Tìm câu hỏi thường gặp phù hợp với tin nhắn của người dùng.
    
    Args:
        user_message (str): Tin nhắn của người dùng
        subject: Đối tượng Subject (tùy chọn)
        topic: Đối tượng Topic (tùy chọn)
        lesson: Đối tượng Lesson (tùy chọn)
        
    Returns:
        ChatbotQuestion: Câu hỏi phù hợp nhất hoặc None nếu không tìm thấy
    """
    try:
        # Chuẩn hóa tin nhắn của người dùng
        user_message = user_message.lower().strip()
        
        # Lọc câu hỏi theo nội dung học tập nếu có
        questions = ChatbotQuestion.objects.filter(is_active=True)
        
        if lesson:
            # Ưu tiên câu hỏi liên quan đến bài học cụ thể
            lesson_questions = questions.filter(lesson=lesson)
            if lesson_questions.exists():
                questions = lesson_questions
        elif topic:
            # Ưu tiên câu hỏi liên quan đến chủ đề con
            topic_questions = questions.filter(category__topic=topic)
            if topic_questions.exists():
                questions = topic_questions
        elif subject:
            # Ưu tiên câu hỏi liên quan đến chủ đề
            subject_questions = questions.filter(category__subject=subject)
            if subject_questions.exists():
                questions = subject_questions
        
        # Tìm câu hỏi phù hợp dựa trên từ khóa
        for question in questions:
            keywords = question.get_keywords_list()
            for keyword in keywords:
                if keyword in user_message:
                    return question
        
        # Nếu không tìm thấy dựa trên từ khóa, sử dụng so khớp văn bản
        best_match = None
        best_ratio = 0.6  # Ngưỡng tối thiểu để coi là phù hợp
        
        for question in questions:
            # So sánh với câu hỏi
            question_text = question.question.lower()
            ratio = difflib.SequenceMatcher(None, user_message, question_text).ratio()
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = question
        
        return best_match
    
    except Exception as e:
        logger.error(f"Lỗi khi tìm câu hỏi phù hợp: {e}")
        return None

def get_fallback_response():
    """
    Trả về câu trả lời mặc định khi không tìm thấy câu hỏi phù hợp.
    
    Returns:
        str: Câu trả lời mặc định
    """
    return """Xin lỗi, tôi không hiểu câu hỏi của bạn. Bạn có thể thử:
1. Đặt câu hỏi rõ ràng hơn
2. Sử dụng các từ khóa liên quan đến nội dung bạn đang tìm kiếm
3. Kiểm tra lỗi chính tả
4. Liên hệ với đội ngũ hỗ trợ nếu bạn cần trợ giúp thêm"""

def get_chatbot_response(conversation, user_message, subject=None, topic=None, lesson=None):
    """
    Lấy phản hồi từ chatbot cho tin nhắn của người dùng.
    
    Args:
        conversation: Đối tượng ChatbotConversation
        user_message: Nội dung tin nhắn của người dùng
        subject: Đối tượng Subject (tùy chọn)
        topic: Đối tượng Topic (tùy chọn)
        lesson: Đối tượng Lesson (tùy chọn)
        
    Returns:
        str: Phản hồi từ chatbot
    """
    try:
        # Lưu tin nhắn của người dùng
        user_msg = ChatbotMessage.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )
        
        # Tìm câu hỏi phù hợp
        matching_question = find_matching_question(user_message, subject, topic, lesson)
        
        # Nếu tìm thấy câu hỏi phù hợp, sử dụng câu trả lời của nó
        if matching_question:
            bot_response = matching_question.answer
            
            # Lưu tin nhắn của chatbot
            bot_msg = ChatbotMessage.objects.create(
                conversation=conversation,
                role='bot',
                content=bot_response,
                matched_question=matching_question
            )
            
            return bot_response
        
        # Nếu không tìm thấy câu hỏi phù hợp, sử dụng câu trả lời mặc định
        fallback_response = get_fallback_response()
        
        # Lưu tin nhắn của chatbot
        bot_msg = ChatbotMessage.objects.create(
            conversation=conversation,
            role='bot',
            content=fallback_response
        )
        
        return fallback_response
    
    except Exception as e:
        logger.error(f"Lỗi khi lấy phản hồi từ chatbot: {e}")
        error_message = "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại sau."
        
        # Lưu tin nhắn lỗi
        ChatbotMessage.objects.create(
            conversation=conversation,
            role='bot',
            content=error_message
        )
        
        return error_message

def get_popular_questions(limit=5, subject=None, topic=None):
    """
    Lấy danh sách câu hỏi phổ biến.
    
    Args:
        limit (int): Số lượng câu hỏi tối đa
        subject: Đối tượng Subject (tùy chọn)
        topic: Đối tượng Topic (tùy chọn)
        
    Returns:
        list: Danh sách câu hỏi phổ biến
    """
    try:
        # Lọc câu hỏi theo nội dung học tập nếu có
        questions = ChatbotQuestion.objects.filter(is_active=True)
        
        if topic:
            # Ưu tiên câu hỏi liên quan đến chủ đề con
            topic_questions = questions.filter(category__topic=topic)
            if topic_questions.exists():
                questions = topic_questions
        elif subject:
            # Ưu tiên câu hỏi liên quan đến chủ đề
            subject_questions = questions.filter(category__subject=subject)
            if subject_questions.exists():
                questions = subject_questions
        
        # Lấy câu hỏi phổ biến dựa trên số lần được khớp
        popular_questions = questions.annotate(
            match_count=models.Count('matched_messages')
        ).order_by('-match_count')[:limit]
        
        return popular_questions
    
    except Exception as e:
        logger.error(f"Lỗi khi lấy câu hỏi phổ biến: {e}")
        return []
