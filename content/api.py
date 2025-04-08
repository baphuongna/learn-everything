from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Subject, Topic, Lesson

def get_topics_by_subject(request, subject_id):
    """API endpoint để lấy danh sách topics theo subject"""
    subject = get_object_or_404(Subject, id=subject_id)
    topics = Topic.objects.filter(subject=subject).order_by('order')

    # Chuyển đổi topics thành danh sách dữ liệu JSON
    topics_data = [
        {
            'id': topic.id,
            'name': topic.name,
            'slug': topic.slug,
            'order': topic.order
        }
        for topic in topics
    ]

    return JsonResponse(topics_data, safe=False)

def get_lessons_by_topic(request, topic_id):
    """API endpoint để lấy danh sách lessons theo topic"""
    topic = get_object_or_404(Topic, id=topic_id)
    lessons = Lesson.objects.filter(topic=topic).order_by('order')

    # Chuyển đổi lessons thành danh sách dữ liệu JSON
    lessons_data = [
        {
            'id': lesson.id,
            'title': lesson.title,
            'slug': lesson.slug,
            'order': lesson.order
        }
        for lesson in lessons
    ]

    return JsonResponse(lessons_data, safe=False)
