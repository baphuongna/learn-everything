from django.urls import path
from . import views

urlpatterns = [
    # Trang chủ Memory Bank
    path('', views.memory_home, name='memory_home'),
    
    # Quản lý danh mục
    path('categories/', views.memory_category_list, name='memory_category_list'),
    path('categories/<slug:slug>/', views.memory_category_detail, name='memory_category_detail'),
    path('categories/<slug:slug>/delete/', views.memory_category_delete, name='memory_category_delete'),
    
    # Quản lý ghi nhớ
    path('items/create/', views.memory_item_create, name='memory_item_create'),
    path('categories/<slug:category_slug>/items/create/', views.memory_item_create, name='memory_item_create_in_category'),
    path('items/<int:pk>/', views.memory_item_detail, name='memory_item_detail'),
    path('items/<int:pk>/edit/', views.memory_item_edit, name='memory_item_edit'),
    path('items/<int:pk>/delete/', views.memory_item_delete, name='memory_item_delete'),
    path('items/<int:pk>/toggle-favorite/', views.memory_item_toggle_favorite, name='memory_item_toggle_favorite'),
    
    # Quản lý tập tin đính kèm
    path('attachments/<int:pk>/delete/', views.memory_attachment_delete, name='memory_attachment_delete'),
    
    # Ôn tập
    path('items/<int:pk>/review/', views.memory_item_review, name='memory_item_review'),
    path('review/', views.memory_review_list, name='memory_review_list'),
    
    # Tìm kiếm
    path('search/', views.memory_search, name='memory_search'),
]
