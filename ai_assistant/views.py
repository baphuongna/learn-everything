from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from content.models import Subject, Topic, Lesson
from .models import AIAssistantChat, AIAssistantMessage, AIAssistantFeedback, AIAssistantPrompt
from .forms import AIAssistantMessageForm, AIAssistantChatForm, AIAssistantFeedbackForm, AIAssistantPromptForm
from .services import get_ai_response, create_new_chat

@login_required
def chat_list(request):
    """Hiển thị danh sách các cuộc trò chuyện với trợ lý AI"""
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    subject_id = request.GET.get('subject', '')
    format_type = request.GET.get('format', '')

    # Lấy danh sách cuộc trò chuyện
    chats = AIAssistantChat.objects.filter(user=request.user).order_by('-updated_at')

    # Áp dụng bộ lọc
    if search_query:
        chats = chats.filter(
            Q(title__icontains=search_query) |
            Q(subject__name__icontains=search_query) |
            Q(topic__name__icontains=search_query) |
            Q(lesson__title__icontains=search_query)
        )

    if subject_id:
        chats = chats.filter(subject_id=subject_id)

    # Lấy danh sách các chủ đề cho bộ lọc
    subjects = Subject.objects.all()

    context = {
        'chats': chats,
        'subjects': subjects,
        'search_query': search_query,
        'selected_subject': subject_id,
        'new_chat_form': AIAssistantChatForm()
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'ai_assistant/chat_list_partial.html', context)

    return render(request, 'ai_assistant/chat_list.html', context)

@login_required
def chat_detail(request, chat_id):
    """Hiển thị chi tiết cuộc trò chuyện với trợ lý AI"""
    chat = get_object_or_404(AIAssistantChat, id=chat_id, user=request.user)
    messages_list = chat.messages.exclude(role='system').order_by('created_at')
    format_type = request.GET.get('format', '')

    # Xử lý gửi tin nhắn mới
    if request.method == 'POST':
        form = AIAssistantMessageForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data['message']

            # Lấy phản hồi từ trợ lý AI
            ai_response = get_ai_response(chat, user_message)

            # Cập nhật thời gian cuộc trò chuyện
            chat.save()  # Tự động cập nhật updated_at

            # Nếu là request HTMX, trả về phần tin nhắn mới
            if request.htmx:
                return render(request, 'ai_assistant/message_exchange.html', {
                    'user_message': user_message,
                    'ai_response': ai_response
                })

            # Nếu không, chuyển hướng về trang chi tiết
            return redirect('ai_assistant:chat_detail', chat_id=chat.id)
    else:
        form = AIAssistantMessageForm()

    context = {
        'chat': chat,
        'messages': messages_list,
        'form': form,
        'feedback_form': AIAssistantFeedbackForm()
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'ai_assistant/chat_detail_partial.html', context)

    return render(request, 'ai_assistant/chat_detail.html', context)

@login_required
def create_chat(request):
    """Tạo cuộc trò chuyện mới với trợ lý AI"""
    if request.method == 'POST':
        form = AIAssistantChatForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            topic = form.cleaned_data.get('topic')
            lesson = form.cleaned_data.get('lesson')
            title = form.cleaned_data.get('title')

            # Tạo cuộc trò chuyện mới
            chat = create_new_chat(request.user, subject, topic, lesson, title)

            if chat:
                messages.success(request, 'Cuộc trò chuyện mới đã được tạo!')
                return redirect('ai_assistant:chat_detail', chat_id=chat.id)
            else:
                messages.error(request, 'Có lỗi xảy ra khi tạo cuộc trò chuyện mới.')
    else:
        form = AIAssistantChatForm()

    return render(request, 'ai_assistant/create_chat.html', {'form': form})

@login_required
def get_topics(request):
    """Lấy danh sách các chủ đề con theo chủ đề chính"""
    subject_id = request.GET.get('subject', '')
    topics = []

    if subject_id:
        topics = Topic.objects.filter(subject_id=subject_id).order_by('order')

    return render(request, 'ai_assistant/topic_options.html', {'topics': topics})

@login_required
def get_lessons(request):
    """Lấy danh sách các bài học theo chủ đề con"""
    topic_id = request.GET.get('topic', '')
    lessons = []

    if topic_id:
        lessons = Lesson.objects.filter(topic_id=topic_id).order_by('order')

    return render(request, 'ai_assistant/lesson_options.html', {'lessons': lessons})

@login_required
def submit_feedback(request, message_id):
    """Gửi phản hồi về câu trả lời của trợ lý AI"""
    message = get_object_or_404(AIAssistantMessage, id=message_id, role='assistant')

    if request.method == 'POST':
        form = AIAssistantFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.message = message
            feedback.user = request.user
            feedback.save()

            messages.success(request, 'Cảm ơn bạn đã gửi phản hồi!')

            # Nếu là request HTMX, trả về thông báo thành công
            if request.htmx:
                return render(request, 'ai_assistant/feedback_success.html')

    return redirect('ai_assistant:chat_detail', chat_id=message.chat.id)

@login_required
def delete_chat(request, chat_id):
    """Xóa cuộc trò chuyện với trợ lý AI"""
    chat = get_object_or_404(AIAssistantChat, id=chat_id, user=request.user)

    if request.method == 'POST':
        chat.delete()
        messages.success(request, 'Cuộc trò chuyện đã được xóa!')

        # Nếu là request HTMX, trả về chuyển hướng
        if request.htmx:
            response = render(request, 'ai_assistant/empty.html')
            response['HX-Redirect'] = request.build_absolute_uri('/ai-assistant/')
            return response

    return redirect('ai_assistant:chat_list')