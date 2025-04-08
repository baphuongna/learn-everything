from django.urls import path
from . import views

app_name = 'advanced_learning'

urlpatterns = [
    # Trang tổng quan (Dashboard)
    path('', views.dashboard, name='dashboard'),
    path('analytics/', views.learning_analytics, name='learning_analytics'),

    # Thông báo
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/count/', views.get_unread_notifications_count, name='get_unread_notifications_count'),

    # Pomodoro Timer
    path('pomodoro/', views.pomodoro_timer, name='pomodoro_timer'),
    path('pomodoro/start/', views.pomodoro_start, name='pomodoro_start'),
    path('pomodoro/end/', views.pomodoro_end, name='pomodoro_end'),
    path('pomodoro/history/', views.pomodoro_history, name='pomodoro_history'),

    # Hệ thống ghi chú Cornell
    path('cornell-notes/', views.cornell_note_list, name='cornell_note_list'),
    path('cornell-notes/create/', views.cornell_note_create, name='cornell_note_create'),
    path('cornell-notes/<int:note_id>/', views.cornell_note_detail, name='cornell_note_detail'),
    path('cornell-notes/<int:note_id>/edit/', views.cornell_note_edit, name='cornell_note_edit'),
    path('cornell-notes/<int:note_id>/delete/', views.cornell_note_delete, name='cornell_note_delete'),

    # Hệ thống Mind Mapping
    path('mind-maps/', views.mind_map_list, name='mind_map_list'),
    path('mind-maps/create/', views.mind_map_create, name='mind_map_create'),
    path('mind-maps/<int:map_id>/', views.mind_map_detail, name='mind_map_detail'),
    path('mind-maps/<int:map_id>/edit/', views.mind_map_edit, name='mind_map_edit'),
    path('mind-maps/<int:map_id>/delete/', views.mind_map_delete, name='mind_map_delete'),

    # Phương pháp Feynman Technique
    path('feynman-notes/', views.feynman_note_list, name='feynman_note_list'),
    path('feynman-notes/create/', views.feynman_note_create, name='feynman_note_create'),
    path('feynman-notes/<int:note_id>/', views.feynman_note_detail, name='feynman_note_detail'),
    path('feynman-notes/<int:note_id>/edit/', views.feynman_note_edit, name='feynman_note_edit'),
    path('feynman-notes/<int:note_id>/delete/', views.feynman_note_delete, name='feynman_note_delete'),

    # Hệ thống học tập dựa trên dự án
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/start/', views.start_project, name='start_project'),
    path('projects/<int:project_id>/update-progress/', views.update_project_progress, name='update_project_progress'),
    path('projects/<int:project_id>/create-mindmap/', views.create_mindmap_from_project, name='create_mindmap_from_project'),
    path('my-projects/', views.my_projects, name='my_projects'),

    # Bài tập thực hành tương tác
    path('exercises/', views.exercise_list, name='exercise_list'),
    path('exercises/<int:exercise_id>/', views.exercise_detail, name='exercise_detail'),
    path('exercises/<int:exercise_id>/submit/', views.submit_exercise, name='submit_exercise'),
    path('exercises/<int:exercise_id>/create-cornell/', views.create_cornell_from_exercise, name='create_cornell_from_exercise'),
    path('exercises/create/', views.create_exercise, name='create_exercise'),
    path('exercises/<int:exercise_id>/edit/', views.edit_exercise, name='edit_exercise'),
    path('exercises/<int:exercise_id>/delete/', views.delete_exercise, name='delete_exercise'),

    # Chế độ thi đấu
    path('competitions/', views.competition_list, name='competition_list'),
    path('competitions/<int:competition_id>/', views.competition_detail, name='competition_detail'),
    path('competitions/<int:competition_id>/join/', views.join_competition, name='join_competition'),
    path('competitions/<int:competition_id>/take/', views.take_competition, name='take_competition'),
    path('competitions/<int:competition_id>/result/', views.competition_result, name='competition_result'),
    path('competitions/<int:competition_id>/create-feynman/', views.create_feynman_from_competition, name='create_feynman_from_competition'),
    path('my-competitions/', views.my_competitions, name='my_competitions'),
    path('competitions/create/', views.create_competition, name='create_competition'),
    path('competitions/<int:competition_id>/edit/', views.edit_competition, name='edit_competition'),
    path('competitions/<int:competition_id>/questions/', views.edit_competition_questions, name='edit_competition_questions'),
    path('competitions/<int:competition_id>/questions/<int:question_id>/answers/', views.edit_question_answers, name='edit_question_answers'),
    path('competitions/<int:competition_id>/delete/', views.delete_competition, name='delete_competition'),
]
