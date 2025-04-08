from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('mark-read/<int:notification_id>/', views.mark_as_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_read'),
    path('preferences/', views.notification_preferences, name='preferences'),
    path('delete/<int:notification_id>/', views.delete_notification, name='delete'),
    path('delete-all/', views.delete_all_notifications, name='delete_all'),
    path('unread-count/', views.get_unread_count, name='unread_count'),
]
