from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from content.models import Subject, Topic, Lesson
from .models import ChatbotCategory, ChatbotQuestion, ChatbotConversation, ChatbotMessage, ChatbotFeedback
from .forms import ChatbotMessageForm, ChatbotFeedbackForm, ChatbotCategoryForm, ChatbotQuestionForm
from .services import create_conversation, get_chatbot_response, get_popular_questions

@login_required
def chatbot_home(request):
    """Trang chủ của chatbot"""
    # Kiểm tra xem người dùng đã có cuộc trò chuyện nào chưa
    conversations = ChatbotConversation.objects.filter(user=request.user, is_active=True).order_by('-updated_at')

    # Lấy cuộc trò chuyện gần nhất hoặc tạo mới
    if conversations.exists():
        conversation = conversations.first()
    else:
        conversation = create_conversation(request.user)

    # Lấy các tin nhắn trong cuộc trò chuyện
    messages_list = conversation.messages.all().order_by('created_at')

    # Lấy các câu hỏi phổ biến
    popular_questions = get_popular_questions(limit=5)

    # Lấy các danh mục câu hỏi
    categories = ChatbotCategory.objects.filter(is_active=True).order_by('order')

    context = {
        'conversation': conversation,
        'messages': messages_list,
        'form': ChatbotMessageForm(),
        'feedback_form': ChatbotFeedbackForm(),
        'popular_questions': popular_questions,
        'categories': categories
    }

    return render(request, 'learning_chatbot/chatbot_home.html', context)

@login_required
def send_message(request, conversation_id):
    """Gửi tin nhắn cho chatbot"""
    conversation = get_object_or_404(ChatbotConversation, id=conversation_id, user=request.user)

    if request.method == 'POST':
        form = ChatbotMessageForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data['message']

            # Lấy phản hồi từ chatbot
            bot_response = get_chatbot_response(conversation, user_message)

            # Cập nhật thời gian cuộc trò chuyện
            conversation.save()  # Tự động cập nhật updated_at

            # Nếu là request HTMX, trả về phần tin nhắn mới
            if request.htmx:
                return render(request, 'learning_chatbot/message_exchange.html', {
                    'user_message': user_message,
                    'bot_response': bot_response,
                    'conversation': conversation
                })

    return redirect('learning_chatbot:chatbot_home')

@login_required
def new_conversation(request):
    """Tạo cuộc trò chuyện mới với chatbot"""
    # Tạo cuộc trò chuyện mới
    conversation = create_conversation(request.user)

    if conversation:
        messages.success(request, 'Cuộc trò chuyện mới đã được tạo!')
    else:
        messages.error(request, 'Có lỗi xảy ra khi tạo cuộc trò chuyện mới.')

    return redirect('learning_chatbot:chatbot_home')

@login_required
def submit_feedback(request, message_id):
    """Gửi phản hồi về câu trả lời của chatbot"""
    message = get_object_or_404(ChatbotMessage, id=message_id, role='bot')

    if request.method == 'POST':
        form = ChatbotFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.message = message
            feedback.user = request.user
            feedback.save()

            messages.success(request, 'Cảm ơn bạn đã gửi phản hồi!')

            # Nếu là request HTMX, trả về thông báo thành công
            if request.htmx:
                return render(request, 'learning_chatbot/feedback_success.html')

    return redirect('learning_chatbot:chatbot_home')

@login_required
def category_questions(request, category_id):
    """Hiển thị các câu hỏi trong danh mục"""
    category = get_object_or_404(ChatbotCategory, id=category_id, is_active=True)
    questions = category.questions.filter(is_active=True).order_by('order')

    context = {
        'category': category,
        'questions': questions
    }

    # Nếu là request HTMX, trả về phần câu hỏi
    if request.htmx:
        return render(request, 'learning_chatbot/category_questions_partial.html', context)

    return render(request, 'learning_chatbot/category_questions.html', context)

@login_required
def question_detail(request, question_id):
    """Hiển thị chi tiết câu hỏi"""
    question = get_object_or_404(ChatbotQuestion, id=question_id, is_active=True)

    context = {
        'question': question
    }

    # Nếu là request HTMX, trả về phần chi tiết câu hỏi
    if request.htmx:
        return render(request, 'learning_chatbot/question_detail_partial.html', context)

    return render(request, 'learning_chatbot/question_detail.html', context)

@login_required
def search_questions(request):
    """Tìm kiếm câu hỏi"""
    search_query = request.GET.get('search', '')

    if search_query:
        questions = ChatbotQuestion.objects.filter(
            Q(question__icontains=search_query) |
            Q(answer__icontains=search_query) |
            Q(keywords__icontains=search_query),
            is_active=True
        ).order_by('category', 'order')
    else:
        questions = ChatbotQuestion.objects.none()

    context = {
        'questions': questions,
        'search_query': search_query
    }

    # Nếu là request HTMX, trả về phần kết quả tìm kiếm
    if request.htmx:
        return render(request, 'learning_chatbot/search_results_partial.html', context)

    return render(request, 'learning_chatbot/search_results.html', context)