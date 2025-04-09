"""
URLs cho ứng dụng quizzes.
"""
from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    
    # URLs cho tự động tạo câu hỏi kiểm tra
    path('auto-generate/', views.auto_generate_quiz, name='auto_generate_quiz'),
    path('get-topics/', views.get_topics, name='get_topics'),
    path('get-lessons/', views.get_lessons, name='get_lessons'),
]
