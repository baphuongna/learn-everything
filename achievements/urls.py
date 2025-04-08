from django.urls import path
from . import views

app_name = 'achievements'

urlpatterns = [
    # Trang tổng quan
    path('', views.achievement_dashboard, name='dashboard'),
    
    # Huy hiệu
    path('badges/', views.badge_list, name='badge_list'),
    
    # Phần thưởng
    path('rewards/', views.reward_list, name='reward_list'),
    path('rewards/<int:reward_id>/redeem/', views.redeem_reward, name='redeem_reward'),
    path('rewards/<int:user_reward_id>/use/', views.use_reward, name='use_reward'),
    
    # Lịch sử điểm thưởng
    path('points/history/', views.point_history, name='point_history'),
]
