"""
URLs cho ứng dụng ai_assistant.
"""
from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('create/', views.create_chat, name='create_chat'),
    path('<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('<int:chat_id>/delete/', views.delete_chat, name='delete_chat'),
    path('feedback/<int:message_id>/', views.submit_feedback, name='submit_feedback'),
    path('get-topics/', views.get_topics, name='get_topics'),
    path('get-lessons/', views.get_lessons, name='get_lessons'),
]
