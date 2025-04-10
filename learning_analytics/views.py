import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# from django.db.models import Q  # Chưa sử dụng
from content.models import Subject, Topic
from .models import AnalyticsPreference, AnalyticsReport, LearningRecommendation
from .forms import AnalyticsPreferenceForm, ReportFilterForm, ShareReportForm
from .services import (
    get_dashboard_data, get_study_time_data, get_quiz_performance_data,
    get_flashcard_performance_data, get_subject_distribution_data,
    get_learning_patterns_data, get_recommendations, get_learning_insights,
    generate_report
)

@login_required
def dashboard(request):
    """Hiển thị bảng điều khiển phân tích dữ liệu học tập"""
    # Lấy dữ liệu cho bảng điều khiển
    dashboard_data = get_dashboard_data(request.user)

    context = {
        'dashboard_data': dashboard_data,
        'last_updated': timezone.now()
    }

    return render(request, 'learning_analytics/dashboard.html', context)

@login_required
def study_time_analysis(request):
    """Hiển thị phân tích thời gian học tập"""
    # Lấy dữ liệu thời gian học tập
    study_time_data = get_study_time_data(request.user)

    context = {
        'study_time_data': study_time_data,
        'last_updated': timezone.now()
    }

    return render(request, 'learning_analytics/study_time_analysis.html', context)

@login_required
def quiz_performance_analysis(request):
    """Hiển thị phân tích hiệu suất bài kiểm tra"""
    # Lấy dữ liệu hiệu suất bài kiểm tra
    quiz_performance_data = get_quiz_performance_data(request.user)

    context = {
        'quiz_performance_data': quiz_performance_data,
        'last_updated': timezone.now()
    }

    return render(request, 'learning_analytics/quiz_performance_analysis.html', context)

@login_required
def flashcard_performance_analysis(request):
    """Hiển thị phân tích hiệu suất flashcard"""
    # Lấy dữ liệu hiệu suất flashcard
    flashcard_performance_data = get_flashcard_performance_data(request.user)

    context = {
        'flashcard_performance_data': flashcard_performance_data,
        'last_updated': timezone.now()
    }

    return render(request, 'learning_analytics/flashcard_performance_analysis.html', context)

@login_required
def subject_distribution_analysis(request):
    """Hiển thị phân tích phân bố thời gian theo chủ đề"""
    # Lấy dữ liệu phân bố thời gian theo chủ đề
    subject_distribution_data = get_subject_distribution_data(request.user)

    context = {
        'subject_distribution_data': subject_distribution_data,
        'last_updated': timezone.now()
    }

    return render(request, 'learning_analytics/subject_distribution_analysis.html', context)

@login_required
def learning_patterns_analysis(request):
    """Hiển thị phân tích mẫu học tập"""
    # Lấy dữ liệu mẫu học tập
    learning_patterns_data = get_learning_patterns_data(request.user)

    context = {
        'learning_patterns_data': learning_patterns_data,
        'last_updated': timezone.now()
    }

    return render(request, 'learning_analytics/learning_patterns_analysis.html', context)

@login_required
def recommendations(request):
    """Hiển thị đề xuất học tập"""
    # Lấy đề xuất học tập
    recommendations_data = get_recommendations(request.user)

    # Lấy danh sách chủ đề
    subject_list = Subject.objects.all().order_by('name')

    context = {
        'recommendations': recommendations_data,
        'subject_list': subject_list,
        'last_updated': timezone.now()
    }

    return render(request, 'learning_analytics/recommendations.html', context)

@login_required
def insights(request):
    """Hiển thị phân tích sâu về học tập"""
    # Lấy phân tích sâu về học tập
    insights_data = get_learning_insights(request.user)

    # Lấy danh sách chủ đề
    subject_list = Subject.objects.all().order_by('name')

    context = {
        'insights': insights_data,
        'subject_list': subject_list,
        'last_updated': timezone.now()
    }

    return render(request, 'learning_analytics/insights.html', context)

@login_required
def reports(request):
    """Hiển thị danh sách báo cáo phân tích"""
    # Lấy danh sách báo cáo
    reports_list = AnalyticsReport.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'reports': reports_list,
        'form': ReportFilterForm()
    }

    return render(request, 'learning_analytics/reports.html', context)

@login_required
def generate_report_view(request):
    """Tạo báo cáo phân tích"""
    if request.method == 'POST':
        form = ReportFilterForm(request.POST)
        if form.is_valid():
            report_type = form.cleaned_data['report_type']
            report_format = form.cleaned_data['report_format']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']

            # Tạo báo cáo
            report = generate_report(
                request.user,
                report_type,
                start_date,
                end_date,
                report_format,
                title,
                description
            )

            if report:
                messages.success(request, 'Báo cáo đã được tạo thành công!')
                return redirect('learning_analytics:report_detail', report_id=report.id)
            else:
                messages.error(request, 'Có lỗi xảy ra khi tạo báo cáo.')
    else:
        form = ReportFilterForm()

    context = {
        'form': form
    }

    return render(request, 'learning_analytics/generate_report.html', context)

@login_required
def report_detail(request, report_id):
    """Hiển thị chi tiết báo cáo phân tích"""
    # Lấy báo cáo
    report = get_object_or_404(AnalyticsReport, id=report_id, user=request.user)

    context = {
        'report': report
    }

    return render(request, 'learning_analytics/report_detail.html', context)

@login_required
def download_report(request, report_id):
    """Tải xuống báo cáo phân tích"""
    # Lấy báo cáo
    report = get_object_or_404(AnalyticsReport, id=report_id, user=request.user)

    # Kiểm tra xem báo cáo đã được tạo chưa
    if not report.is_generated:
        messages.error(request, 'Báo cáo chưa được tạo.')
        return redirect('learning_analytics:report_detail', report_id=report.id)

    # Tải xuống báo cáo
    if report.report_format == 'html':
        return render(request, 'learning_analytics/report_download.html', {'report': report})
    elif report.report_format == 'pdf':
        # Xử lý tải xuống PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report.title}.pdf"'
        # ... Xử lý tạo PDF ...
        return response
    elif report.report_format == 'csv':
        # Xử lý tải xuống CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report.title}.csv"'
        # ... Xử lý tạo CSV ...
        return response
    elif report.report_format == 'json':
        # Xử lý tải xuống JSON
        return JsonResponse(report.report_data)

    messages.error(request, 'Định dạng báo cáo không hợp lệ.')
    return redirect('learning_analytics:report_detail', report_id=report.id)

@login_required
def preferences(request):
    """Hiển thị và cập nhật tùy chọn phân tích"""
    # Lấy tùy chọn phân tích của người dùng
    preferences, _ = AnalyticsPreference.objects.get_or_create(
        user=request.user,
        defaults={
            'show_study_time': True,
            'show_quiz_performance': True,
            'show_flashcard_performance': True,
            'show_subject_distribution': True,
            'show_learning_patterns': True,
            'show_recommendations': True,
            'dashboard_refresh_rate': 24
        }
    )

    if request.method == 'POST':
        form = AnalyticsPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tùy chọn phân tích đã được cập nhật!')
            return redirect('learning_analytics:dashboard')
    else:
        form = AnalyticsPreferenceForm(instance=preferences)

    context = {
        'form': form
    }

    return render(request, 'learning_analytics/preferences.html', context)

@login_required
def dismiss_recommendation(request, recommendation_id):
    """Bỏ qua đề xuất học tập"""
    # Lấy đề xuất
    recommendation = get_object_or_404(LearningRecommendation, id=recommendation_id, user=request.user)

    # Đánh dấu đã bỏ qua
    recommendation.is_dismissed = True
    recommendation.save()

    messages.success(request, 'Đề xuất đã được bỏ qua!')

    # Nếu là request HTMX, trả về thông báo thành công
    if request.htmx:
        return HttpResponse('<div class="alert alert-success">\u0110\u1ec1 xu\u1ea5t \u0111\u00e3 \u0111\u01b0\u1ee3c b\u1ecf qua!</div>')

    return redirect('learning_analytics:recommendations')

@login_required
def complete_recommendation(request, recommendation_id):
    """Đánh dấu đề xuất học tập đã hoàn thành"""
    # Lấy đề xuất
    recommendation = get_object_or_404(LearningRecommendation, id=recommendation_id, user=request.user)

    # Đánh dấu đã hoàn thành
    recommendation.is_completed = True
    recommendation.save()

    messages.success(request, 'Đề xuất đã được đánh dấu hoàn thành!')

    # Nếu là request HTMX, trả về thông báo thành công
    if request.htmx:
        return HttpResponse('<div class="alert alert-success">\u0110\u1ec1 xu\u1ea5t \u0111\u00e3 \u0111\u01b0\u1ee3c \u0111\u00e1nh d\u1ea5u ho\u00e0n th\u00e0nh!</div>')

    return redirect('learning_analytics:recommendations')

@login_required
def share_report(request, report_id):
    """
    Chia sẻ báo cáo phân tích qua email.
    """
    report = get_object_or_404(AnalyticsReport, id=report_id, user=request.user)

    if request.method == 'POST':
        form = ShareReportForm(request.POST)
        if form.is_valid():
            recipient_email = form.cleaned_data['recipient_email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            attach_file = form.cleaned_data['attach_file']

            # Tạo email
            email = EmailMessage(
                subject=subject,
                body=render_to_string('learning_analytics/email/share_report_email.html', {
                    'report': report,
                    'message': message,
                    'user': request.user,
                    'site_url': request.build_absolute_uri('/')[:-1]
                }),
                from_email=None,  # Sử dụng email mặc định của hệ thống
                to=[recipient_email]
            )

            # Đính kèm file nếu có yêu cầu
            if attach_file and report.file_path:
                try:
                    with open(report.file_path, 'rb') as f:
                        email.attach(os.path.basename(report.file_path), f.read(), 'application/octet-stream')
                except Exception as e:
                    messages.error(request, f"Không thể đính kèm file báo cáo: {e}")

            # Gửi email
            try:
                email.send()
                messages.success(request, f"Báo cáo đã được gửi đến {recipient_email}")
                return redirect('learning_analytics:report_detail', report_id=report.id)
            except Exception as e:
                messages.error(request, f"Không thể gửi email: {e}")
    else:
        form = ShareReportForm()

    return render(request, 'learning_analytics/share_report.html', {
        'form': form,
        'report': report
    })

@login_required
def get_topics(request):
    """Lấy danh sách các chủ đề con theo chủ đề chính"""
    subject_id = request.GET.get('subject', '')
    topics = []

    if subject_id:
        topics = Topic.objects.filter(subject_id=subject_id).order_by('order')

    return render(request, 'learning_analytics/topic_options.html', {'topics': topics})