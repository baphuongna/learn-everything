from django.urls import path
from . import views
from . import api

app_name = 'learning_goals'

urlpatterns = [
    # Trang tổng quan
    path('dashboard/', views.goal_dashboard, name='dashboard'),

    # Quản lý mục tiêu
    path('', views.goal_list, name='goal_list'),
    path('<int:goal_id>/', views.goal_detail, name='goal_detail'),
    path('create/', views.goal_create, name='goal_create'),
    path('<int:goal_id>/edit/', views.goal_edit, name='goal_edit'),
    path('<int:goal_id>/delete/', views.goal_delete, name='goal_delete'),

    # Cập nhật tiến độ
    path('<int:goal_id>/update-progress/', views.update_progress, name='update_progress'),

    # Xuất mục tiêu
    path('<int:goal_id>/export-ical/', views.export_goal_ical, name='export_goal_ical'),

    # Chia sẻ mục tiêu
    path('invitation/<int:invitation_id>/<str:action>/', views.handle_invitation, name='handle_invitation'),

    # API endpoints
    path('api/goal/<int:goal_id>/progress-data/', api.goal_progress_data, name='api_goal_progress_data'),
    path('api/goal-completion-stats/', api.goal_completion_stats, name='api_goal_completion_stats'),
    path('api/goal-category-stats/', api.goal_category_stats, name='api_goal_category_stats'),
    path('api/goal-streak-data/', api.goal_streak_data, name='api_goal_streak_data'),
]
