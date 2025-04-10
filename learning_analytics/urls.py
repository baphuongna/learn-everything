"""
URLs cho ứng dụng learning_analytics.
"""
from django.urls import path
from . import views

app_name = 'learning_analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('study-time/', views.study_time_analysis, name='study_time_analysis'),
    path('quiz-performance/', views.quiz_performance_analysis, name='quiz_performance_analysis'),
    path('flashcard-performance/', views.flashcard_performance_analysis, name='flashcard_performance_analysis'),
    path('subject-distribution/', views.subject_distribution_analysis, name='subject_distribution_analysis'),
    path('learning-patterns/', views.learning_patterns_analysis, name='learning_patterns_analysis'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('insights/', views.insights, name='insights'),
    path('reports/', views.reports, name='reports'),
    path('reports/generate/', views.generate_report_view, name='generate_report'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_id>/download/', views.download_report, name='download_report'),
    path('reports/<int:report_id>/share/', views.share_report, name='share_report'),
    path('preferences/', views.preferences, name='preferences'),
    path('recommendations/<int:recommendation_id>/dismiss/', views.dismiss_recommendation, name='dismiss_recommendation'),
    path('recommendations/<int:recommendation_id>/complete/', views.complete_recommendation, name='complete_recommendation'),
    path('get-topics/', views.get_topics, name='get_topics'),
]
