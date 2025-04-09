from django.urls import path
from . import views

urlpatterns = [
    path('', views.integration_home, name='note_integration_home'),
    path('connect/<str:provider>/', views.connect_account, name='note_integration_connect'),
    path('callback/', views.auth_callback, name='note_integration_callback'),
    path('disconnect/<int:account_id>/', views.disconnect_account, name='note_integration_disconnect'),
    path('account/<int:account_id>/', views.account_details, name='note_integration_account_details'),
    path('sync-note/', views.sync_note, name='note_integration_sync_note'),
    path('get-sections/', views.get_sections, name='note_integration_get_sections'),
]
