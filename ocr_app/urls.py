from django.urls import path
from . import views

urlpatterns = [
    path('', views.ocr_home, name='ocr_home'),
    path('upload/', views.upload_image, name='ocr_upload'),
    path('result/<int:result_id>/', views.ocr_result, name='ocr_result'),
    path('history/', views.ocr_history, name='ocr_history'),
]
