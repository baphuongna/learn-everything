from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='personalization_dashboard'),
    
    # Lộ trình học tập
    path('learning-pathways/', views.learning_pathway_list, name='learning_pathway_list'),
    path('learning-pathways/<int:pathway_id>/', views.learning_pathway_detail, name='learning_pathway_detail'),
    path('learning-pathways/create/', views.learning_pathway_create, name='learning_pathway_create'),
    path('learning-pathways/<int:pathway_id>/update/', views.learning_pathway_update, name='learning_pathway_update'),
    path('learning-pathways/<int:pathway_id>/delete/', views.learning_pathway_delete, name='learning_pathway_delete'),
    
    # Bước trong lộ trình
    path('learning-pathways/<int:pathway_id>/steps/create/', views.pathway_step_create, name='pathway_step_create'),
    path('pathway-steps/<int:step_id>/update/', views.pathway_step_update, name='pathway_step_update'),
    path('pathway-steps/<int:step_id>/delete/', views.pathway_step_delete, name='pathway_step_delete'),
    path('pathway-steps/<int:step_id>/complete/', views.pathway_step_complete, name='pathway_step_complete'),
    
    # Sở thích học tập
    path('learning-preferences/', views.learning_preference, name='learning_preference'),
    
    # Tùy chỉnh giao diện
    path('ui-preferences/', views.ui_preference, name='ui_preference'),
    
    # Nhắc nhở học tập
    path('study-reminders/', views.study_reminder_list, name='study_reminder_list'),
    path('study-reminders/create/', views.study_reminder_create, name='study_reminder_create'),
    path('study-reminders/<int:reminder_id>/update/', views.study_reminder_update, name='study_reminder_update'),
    path('study-reminders/<int:reminder_id>/delete/', views.study_reminder_delete, name='study_reminder_delete'),
    path('study-reminders/<int:reminder_id>/toggle/', views.study_reminder_toggle, name='study_reminder_toggle'),
    
    # Điểm mạnh/yếu
    path('strengths-weaknesses/', views.strength_weakness_list, name='strength_weakness_list'),
    path('strengths-weaknesses/create/', views.strength_weakness_create, name='strength_weakness_create'),
    path('strengths-weaknesses/<int:assessment_id>/update/', views.strength_weakness_update, name='strength_weakness_update'),
    path('strengths-weaknesses/<int:assessment_id>/delete/', views.strength_weakness_delete, name='strength_weakness_delete'),
    
    # Đề xuất nội dung
    path('recommendations/', views.content_recommendation_list, name='content_recommendation_list'),
    path('recommendations/<int:recommendation_id>/', views.content_recommendation_detail, name='content_recommendation_detail'),
    path('recommendations/<int:recommendation_id>/feedback/', views.content_recommendation_feedback, name='content_recommendation_feedback'),
    
    # API endpoints
    path('api/get-topics-by-subject/', views.get_topics_by_subject, name='get_topics_by_subject'),
]
