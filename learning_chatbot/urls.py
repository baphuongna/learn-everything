"""
URLs cho ứng dụng learning_chatbot.
"""
from django.urls import path
from . import views

app_name = 'learning_chatbot'

urlpatterns = [
    path('', views.chatbot_home, name='chatbot_home'),
    path('send/<int:conversation_id>/', views.send_message, name='send_message'),
    path('new/', views.new_conversation, name='new_conversation'),
    path('feedback/<int:message_id>/', views.submit_feedback, name='submit_feedback'),
    path('category/<int:category_id>/', views.category_questions, name='category_questions'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('search/', views.search_questions, name='search_questions'),
]
