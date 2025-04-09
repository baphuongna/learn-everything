"""
URLs cho ứng dụng flashcards.
"""
from django.urls import path
from . import views

app_name = 'flashcards'

urlpatterns = [
    path('', views.flashcard_list, name='flashcard_list'),
    path('<int:flashcard_set_id>/', views.flashcard_set_detail, name='flashcard_set_detail'),
    path('update-recall-level/', views.update_recall_level, name='update_recall_level'),
    path('due/', views.due_flashcards, name='due_flashcards'),

    # URLs cho tự động tạo flashcard
    path('auto-generate/', views.auto_generate_flashcards, name='auto_generate_flashcards'),
    path('get-topics/', views.get_topics, name='get_topics'),
    path('get-lessons/', views.get_lessons, name='get_lessons'),

    # URLs cho tạo flashcard từ văn bản
    path('text-to-flashcards/', views.text_to_flashcards, name='text_to_flashcards'),
    path('preview-text-flashcards/', views.preview_text_flashcards, name='preview_text_flashcards'),

    # API endpoints
    path('get-subjects/', views.get_subjects, name='get_subjects'),
]
