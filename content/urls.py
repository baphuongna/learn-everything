from django.urls import path
from . import views
from . import api

app_name = 'content'

urlpatterns = [
    # API endpoints
    path('api/subjects/<int:subject_id>/topics/', api.get_topics_by_subject, name='get_topics_by_subject'),
    path('api/topics/<int:topic_id>/lessons/', api.get_lessons_by_topic, name='get_lessons_by_topic'),
]
