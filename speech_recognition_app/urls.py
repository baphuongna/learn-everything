from django.urls import path
from . import views

urlpatterns = [
    path('', views.speech_recognition_home, name='speech_recognition_home'),
    path('upload/', views.upload_audio, name='speech_recognition_upload'),
    path('record/', views.record_audio, name='speech_recognition_record'),
    path('process-recording/', views.process_recorded_audio, name='speech_recognition_process_recording'),
    path('result/<int:result_id>/', views.speech_recognition_result, name='speech_recognition_result'),
    path('history/', views.speech_recognition_history, name='speech_recognition_history'),

    # Đánh giá phát âm
    path('pronunciation/', views.pronunciation_evaluation, name='pronunciation_evaluation'),
    path('pronunciation/evaluate/', views.evaluate_pronunciation, name='evaluate_pronunciation'),
    path('pronunciation/result/<int:result_id>/', views.pronunciation_evaluation_result, name='pronunciation_evaluation_result'),
    path('pronunciation/history/', views.pronunciation_history, name='pronunciation_history'),
]
