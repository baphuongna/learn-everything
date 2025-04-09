"""
URL configuration for learning_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from content import views as content_views
from accounts import views as accounts_views
from flashcards import views as flashcards_views
from quizzes import views as quizzes_views

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Content
    path("", content_views.home, name="home"),
    path("about/", content_views.about, name="about"),
    path("subjects/", content_views.subject_list, name="subject_list"),
    path("subjects/<slug:slug>/", content_views.subject_detail, name="subject_detail"),
    path("subjects/<slug:subject_slug>/topics/<slug:topic_slug>/lessons/<slug:lesson_slug>/",
         content_views.lesson_detail, name="lesson_detail"),
    path("mark-lesson-complete/<int:lesson_id>/", content_views.mark_lesson_complete, name="mark_lesson_complete"),
    path("toggle-favorite-subject/<int:subject_id>/", content_views.toggle_favorite_subject, name="toggle_favorite_subject"),

    # Accounts
    path("accounts/register/", accounts_views.register, name="register"),
    path("accounts/login/", accounts_views.CustomLoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/profile/", accounts_views.profile, name="profile"),
    path("accounts/progress/", accounts_views.progress, name="progress"),
    path("accounts/record-study-session/", accounts_views.record_study_session, name="record_study_session"),
    path("accounts/password-reset/",
         auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
         name="password_reset"),
    path("accounts/password-reset/done/",
         auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"),
         name="password_reset_done"),
    path("accounts/password-reset-confirm/<uidb64>/<token>/",
         auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"),
         name="password_reset_confirm"),
    path("accounts/password-reset-complete/",
         auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"),
         name="password_reset_complete"),

    # Flashcards
    path("flashcards/", include("flashcards.urls")),

    # Quizzes
    path("quizzes/", include("quizzes.urls")),

    # Memory Bank
    path("memory/", include("memory_bank.urls")),

    # Advanced Learning Features
    path("advanced/", include("advanced_learning.urls")),

    # Content API
    path("", include("content.urls")),

    # Summernote Editor
    path('summernote/', include('django_summernote.urls')),

    # Notifications
    path('notifications/', include('notifications.urls')),

    # Learning Goals
    path('learning-goals/', include('learning_goals.urls')),

    # Achievements
    path('achievements/', include('achievements.urls')),

    # Personalization
    path('personalization/', include('personalization.urls')),

    # AI Assistant
    path('ai-assistant/', include('ai_assistant.urls')),

    # Learning Chatbot
    path('chatbot/', include('learning_chatbot.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
