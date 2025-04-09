from django.urls import path
from . import views
from . import views_learning_goals
from . import api

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
    path('pomodoro/get-topics/', views.get_topics, name='get_topics'),

    # Hệ thống ghi chú Cornell
    path('cornell-notes/', views.cornell_note_list, name='cornell_note_list'),
    path('cornell-notes/create/', views.cornell_note_create, name='cornell_note_create'),
    path('cornell-notes/<int:note_id>/', views.cornell_note_detail, name='cornell_note_detail'),
    path('cornell-notes/<int:note_id>/edit/', views.cornell_note_edit, name='cornell_note_edit'),
    path('cornell-notes/<int:note_id>/delete/', views.cornell_note_delete, name='cornell_note_delete'),
    # Tính năng mới cho Cornell Notes
    path('cornell-notes/<int:note_id>/export-pdf/', views.cornell_note_export_pdf, name='cornell_note_export_pdf'),
    path('cornell-notes/<int:note_id>/share/', views.cornell_note_share, name='cornell_note_share'),
    path('cornell-notes/shared/<str:share_url>/', views.cornell_note_shared_view, name='cornell_note_shared_view'),
    path('cornell-notes/<int:note_id>/review/', views.cornell_note_review, name='cornell_note_review'),
    path('cornell-notes/to-review/', views.cornell_notes_to_review, name='cornell_notes_to_review'),
    path('cornell-notes/<int:note_id>/create-flashcards/', views.cornell_note_create_flashcards, name='cornell_note_create_flashcards'),
    path('cornell-notes/<int:note_id>/create-quiz/', views.cornell_note_create_quiz, name='cornell_note_create_quiz'),

    # Hệ thống Mind Mapping
    path('mind-maps/', views.mind_map_list, name='mind_map_list'),
    path('mind-maps/create/', views.mind_map_create, name='mind_map_create'),
    path('mind-maps/<int:map_id>/', views.mind_map_detail, name='mind_map_detail'),
    path('mind-maps/<int:map_id>/edit/', views.mind_map_edit, name='mind_map_edit'),
    path('mind-maps/<int:map_id>/delete/', views.mind_map_delete, name='mind_map_delete'),
    # Tính năng mới cho Mind Mapping
    path('mind-maps/<int:map_id>/export-image/', views.mind_map_export_image, name='mind_map_export_image'),
    path('mind-maps/<int:map_id>/export-pdf/', views.mind_map_export_pdf, name='mind_map_export_pdf'),
    path('mind-maps/<int:map_id>/share/', views.mind_map_share, name='mind_map_share'),
    path('mind-maps/shared/<str:share_url>/', views.mind_map_shared_view, name='mind_map_shared_view'),
    path('mind-maps/<int:map_id>/create-flashcards/', views.mind_map_create_flashcards, name='mind_map_create_flashcards'),
    path('mind-maps/<int:map_id>/create-quiz/', views.mind_map_create_quiz, name='mind_map_create_quiz'),
    path('mind-maps/<int:map_id>/create-cornell-note/', views.mind_map_create_cornell_note, name='mind_map_create_cornell_note'),

    # Phương pháp Feynman Technique
    path('feynman-notes/', views.feynman_note_list, name='feynman_note_list'),
    path('feynman-notes/create/', views.feynman_note_create, name='feynman_note_create'),
    path('feynman-notes/<int:note_id>/', views.feynman_note_detail, name='feynman_note_detail'),
    path('feynman-notes/<int:note_id>/edit/', views.feynman_note_edit, name='feynman_note_edit'),
    path('feynman-notes/<int:note_id>/delete/', views.feynman_note_delete, name='feynman_note_delete'),
    # Tính năng mới cho Feynman Technique
    path('feynman-notes/<int:note_id>/export-pdf/', views.feynman_note_export_pdf, name='feynman_note_export_pdf'),
    path('feynman-notes/<int:note_id>/share/', views.feynman_note_share, name='feynman_note_share'),
    path('feynman-notes/shared/<str:share_url>/', views.feynman_note_shared_view, name='feynman_note_shared_view'),
    path('feynman-notes/<int:note_id>/review/', views.feynman_note_review, name='feynman_note_review'),
    path('feynman-notes/to-review/', views.feynman_notes_to_review, name='feynman_notes_to_review'),
    path('feynman-notes/<int:note_id>/create-flashcards/', views.feynman_note_create_flashcards, name='feynman_note_create_flashcards'),
    path('feynman-notes/<int:note_id>/create-quiz/', views.feynman_note_create_quiz, name='feynman_note_create_quiz'),
    path('feynman-notes/<int:note_id>/create-mindmap/', views.feynman_note_create_mindmap, name='feynman_note_create_mindmap'),

    # Hệ thống học tập dựa trên dự án
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/start/', views.start_project, name='start_project'),
    path('projects/<int:project_id>/update-progress/', views.update_project_progress, name='update_project_progress'),
    path('projects/<int:project_id>/create-mindmap/', views.create_mindmap_from_project, name='create_mindmap_from_project'),
    path('my-projects/', views.my_projects, name='my_projects'),
    # Tính năng mới cho hệ thống học tập dựa trên dự án
    path('projects/<int:project_id>/upload-result/', views.upload_project_result, name='upload_project_result'),
    path('projects/<int:project_id>/comment/', views.add_project_comment, name='add_project_comment'),
    path('projects/<int:project_id>/share/', views.share_project, name='share_project'),
    path('projects/shared/<str:share_url>/', views.shared_project_view, name='shared_project_view'),
    path('projects/<int:project_id>/link-flashcards/', views.link_project_flashcards, name='link_project_flashcards'),
    path('projects/<int:project_id>/link-quiz/', views.link_project_quiz, name='link_project_quiz'),
    path('projects/<int:project_id>/link-pomodoro/', views.link_project_pomodoro, name='link_project_pomodoro'),

    # Bài tập thực hành tương tác
    path('exercises/', views.exercise_list, name='exercise_list'),
    path('exercises/<int:exercise_id>/', views.exercise_detail, name='exercise_detail'),
    path('exercises/<int:exercise_id>/submit/', views.submit_exercise, name='submit_exercise'),
    path('exercises/<int:exercise_id>/create-cornell/', views.create_cornell_from_exercise, name='create_cornell_from_exercise'),
    path('exercises/create/', views.create_exercise, name='create_exercise'),
    path('exercises/<int:exercise_id>/edit/', views.edit_exercise, name='edit_exercise'),
    path('exercises/<int:exercise_id>/delete/', views.delete_exercise, name='delete_exercise'),
    # Tính năng mới cho bài tập thực hành tương tác
    path('exercises/<int:exercise_id>/run-code/', views.run_code, name='run_code'),
    path('exercises/<int:exercise_id>/get-hint/', views.get_exercise_hint, name='get_exercise_hint'),
    path('exercises/<int:exercise_id>/submissions/', views.exercise_submissions, name='exercise_submissions'),
    path('exercises/<int:exercise_id>/link-achievement/', views.link_exercise_achievement, name='link_exercise_achievement'),
    path('exercises/my-submissions/', views.my_exercise_submissions, name='my_exercise_submissions'),
    path('exercises/leaderboard/', views.exercise_leaderboard, name='exercise_leaderboard'),

    # Chế độ thi đấu
    path('competitions/', views.competition_list, name='competition_list'),
    path('competitions/<int:competition_id>/', views.competition_detail, name='competition_detail'),
    path('competitions/<int:competition_id>/leaderboard/', views.competition_leaderboard, name='competition_leaderboard'),
    path('competitions/<int:competition_id>/participants/', views.competition_participants, name='competition_participants'),
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
    # Tính năng mới cho chế độ thi đấu
    path('competitions/leaderboard/', views.competition_leaderboard, name='competition_leaderboard'),
    path('competitions/achievements/', views.competition_achievements, name='competition_achievements'),
    path('competitions/<int:competition_id>/share/', views.share_competition_result, name='share_competition_result'),
    path('competitions/<int:competition_id>/share-image/', views.generate_share_image, name='generate_share_image'),
    path('competitions/subscribe/', views.subscribe_competition_notifications, name='subscribe_competition_notifications'),
    path('competitions/unsubscribe/', views.unsubscribe_competition_notifications, name='unsubscribe_competition_notifications'),
    path('competitions/subscriptions/', views.my_competition_subscriptions, name='my_competition_subscriptions'),

    # Chế độ thi đấu trực tiếp
    path('live-competitions/', views.live_competitions, name='live_competitions'),
    path('live-competitions/create/', views.create_live_competition, name='create_live_competition'),
    path('live-competitions/create/<int:competition_id>/', views.create_live_competition, name='create_live_competition_from_competition'),
    path('live-competitions/<int:live_competition_id>/', views.live_competition_detail, name='live_competition_detail'),
    path('live-competitions/<int:live_competition_id>/join/', views.join_live_competition, name='join_live_competition'),
    path('live-competitions/<int:live_competition_id>/leave/', views.leave_live_competition, name='leave_live_competition'),
    path('live-competitions/<int:live_competition_id>/start/', views.start_live_competition, name='start_live_competition'),
    path('live-competitions/<int:live_competition_id>/next-question/', views.next_question, name='next_question'),
    path('live-competitions/<int:live_competition_id>/submit-answer/', views.submit_live_answer, name='submit_live_answer'),
    path('live-competitions/<int:live_competition_id>/end/', views.end_live_competition, name='end_live_competition'),
    path('live-competitions/<int:live_competition_id>/cancel/', views.cancel_live_competition, name='cancel_live_competition'),

    # Chế độ thi đấu theo nhóm
    path('competition-teams/', views.competition_teams, name='competition_teams'),
    path('competition-teams/create/', views.create_team, name='create_team'),
    path('competition-teams/create/<int:competition_id>/', views.create_team, name='create_team_from_competition'),
    path('competition-teams/<int:team_id>/', views.team_detail, name='team_detail'),
    path('competition-teams/<int:team_id>/join/', views.join_team, name='join_team'),
    path('competition-teams/<int:team_id>/leave/', views.leave_team, name='leave_team'),
    path('competition-teams/<int:team_id>/remove-member/<int:user_id>/', views.remove_member, name='remove_member'),
    path('competition-teams/<int:team_id>/transfer-leadership/<int:user_id>/', views.transfer_leadership, name='transfer_leadership'),
    path('competition-teams/<int:team_id>/disband/', views.disband_team, name='disband_team'),

    # Mục tiêu học tập và theo dõi thời gian học tập
    path('learning-goals/', views_learning_goals.learning_goals, name='learning_goals'),
    path('learning-goals/create/', views_learning_goals.create_learning_goal, name='create_learning_goal'),
    path('learning-goals/<int:goal_id>/edit/', views_learning_goals.edit_learning_goal, name='edit_learning_goal'),
    path('learning-goals/<int:goal_id>/delete/', views_learning_goals.delete_learning_goal, name='delete_learning_goal'),
    path('learning-goals/<int:goal_id>/complete/', views_learning_goals.complete_learning_goal, name='complete_learning_goal'),
    path('learning-goals/<int:goal_id>/reactivate/', views_learning_goals.reactivate_learning_goal, name='reactivate_learning_goal'),
    path('learning-goals/<int:goal_id>/update-progress/', views_learning_goals.update_learning_goal_progress, name='update_learning_goal_progress'),
    path('daily-study-log/', views_learning_goals.daily_study_log, name='daily_study_log'),
    path('add-study-time/', views_learning_goals.add_study_time, name='add_study_time'),

    # API endpoints
    path('api/learning-goals/', api.api_learning_goals, name='api_learning_goals'),
    path('api/learning-goals/create/', api.api_create_learning_goal, name='api_create_learning_goal'),
    path('api/learning-goals/<int:goal_id>/update/', api.api_update_learning_goal, name='api_update_learning_goal'),
    path('api/learning-goals/<int:goal_id>/delete/', api.api_delete_learning_goal, name='api_delete_learning_goal'),
    path('api/daily-study-logs/', api.api_daily_study_logs, name='api_daily_study_logs'),
    path('api/add-study-time/', api.api_add_study_time, name='api_add_study_time'),
    path('api/learning-statistics/', api.api_learning_statistics, name='api_learning_statistics'),
    path('api/learning-features/', api.api_learning_features, name='api_learning_features'),
]
