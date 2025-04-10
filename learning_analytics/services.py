"""
Dịch vụ phân tích dữ liệu học tập.
"""
import logging
import datetime
import os
import csv
import base64
from io import BytesIO, StringIO
from django.db.models import Sum
from django.utils import timezone
from django.template.loader import get_template
from django.conf import settings
from content.models import Subject, Lesson
from quizzes.models import Quiz, QuizAttempt
from flashcards.models import FlashcardSet, SpacedRepetitionSchedule
from accounts.models import StudySession
from .models import AnalyticsPreference, AnalyticsReport

logger = logging.getLogger(__name__)

# Thư viện matplotlib để tạo biểu đồ
try:
    import matplotlib
    matplotlib.use('Agg')  # Sử dụng backend không cần hiển thị
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_SUPPORT = True
except ImportError:
    MATPLOTLIB_SUPPORT = False
    logger.warning("matplotlib không được cài đặt. Tính năng tạo biểu đồ sẽ không hoạt động.")

# Thư viện xhtml2pdf để tạo file PDF
try:
    from xhtml2pdf import pisa
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logger.warning("xhtml2pdf không được cài đặt. Tính năng xuất PDF sẽ không hoạt động.")

def generate_csv_report(report):
    """
    Tạo báo cáo dạng CSV.

    Args:
        report: Đối tượng AnalyticsReport

    Returns:
        StringIO: Đối tượng StringIO chứa nội dung CSV
    """
    try:
        # Tạo file CSV
        output = StringIO()
        writer = csv.writer(output)

        # Thông tin báo cáo
        writer.writerow(['BÁO CÁO PHÂN TÍCH HỌC TẬP'])
        writer.writerow([f'Tiêu đề: {report.title}'])
        writer.writerow([f'Mô tả: {report.description}'])
        writer.writerow([f'Thời gian: {report.start_date.strftime("%d/%m/%Y")} - {report.end_date.strftime("%d/%m/%Y")}'])
        writer.writerow([])

        # Thời gian học tập
        writer.writerow(['THỜI GIAN HỌC TẬP'])
        writer.writerow(['Tổng thời gian học tập (giờ)', f"{report.report_data['study_time']['total_study_time']:.1f}"])
        writer.writerow(['Trung bình hàng ngày (giờ/ngày)', f"{report.report_data['study_time']['daily_average']:.1f}"])
        writer.writerow(['Trung bình hàng tuần (giờ/tuần)', f"{report.report_data['study_time']['weekly_average']:.1f}"])
        writer.writerow(['Trung bình hàng tháng (giờ/tháng)', f"{report.report_data['study_time']['monthly_average']:.1f}"])
        writer.writerow([])

        # Thời gian học tập theo chủ đề
        writer.writerow(['THỜI GIAN HỌC TẬP THEO CHỦ ĐỀ'])
        writer.writerow(['Chủ đề', 'Thời gian (giờ)', 'Phần trăm'])
        for subject in report.report_data['study_time']['study_time_by_subject']:
            writer.writerow([subject['subject_name'], f"{subject['study_time']:.1f}", f"{subject['percentage']:.1f}%"])
        writer.writerow([])

        # Hiệu suất bài kiểm tra
        writer.writerow(['HIỆU SUẤT BÀI KIỂM TRA'])
        writer.writerow(['Điểm trung bình', f"{report.report_data['quiz_performance']['average_score']:.1f}%"])
        writer.writerow(['Tổng số bài kiểm tra', report.report_data['quiz_performance']['total_quizzes']])
        writer.writerow(['Tổng số câu hỏi', report.report_data['quiz_performance']['total_questions']])
        writer.writerow(['Câu trả lời đúng', report.report_data['quiz_performance']['correct_answers']])
        writer.writerow([])

        # Điểm bài kiểm tra theo chủ đề
        writer.writerow(['ĐIỂM BÀI KIỂM TRA THEO CHỦ ĐỀ'])
        writer.writerow(['Chủ đề', 'Điểm trung bình', 'Số bài kiểm tra'])
        for subject in report.report_data['quiz_performance']['quiz_scores_by_subject']:
            writer.writerow([subject['subject_name'], f"{subject['score']:.1f}%", subject['total_quizzes']])
        writer.writerow([])

        # Hiệu suất flashcard
        writer.writerow(['HIỆU SUẤT FLASHCARD'])
        writer.writerow(['Tỷ lệ ghi nhớ', f"{report.report_data['flashcard_performance']['retention_rate']:.1f}%"])
        writer.writerow(['Tổng số thẻ', report.report_data['flashcard_performance']['total_cards']])
        writer.writerow(['Thẻ đã thành thạo', report.report_data['flashcard_performance']['mastered_cards']])
        writer.writerow(['Thẻ đang học', report.report_data['flashcard_performance']['learning_cards']])
        writer.writerow([])

        # Tỷ lệ ghi nhớ theo chủ đề
        writer.writerow(['TỶ LỆ GHI NHỚ THEO CHỦ ĐỀ'])
        writer.writerow(['Chủ đề', 'Tỷ lệ ghi nhớ', 'Thẻ đã thành thạo', 'Tổng số thẻ'])
        for subject in report.report_data['flashcard_performance']['retention_by_subject']:
            writer.writerow([subject['subject_name'], f"{subject['retention_rate']:.1f}%", subject['mastered_cards'], subject['total_cards']])
        writer.writerow([])

        # Phân tích sâu
        writer.writerow(['PHÂN TÍCH SÂU'])
        for insight in report.report_data['insights']:
            writer.writerow([insight['title']])
            writer.writerow([insight['description']])
            writer.writerow([])

        # Đề xuất học tập
        writer.writerow(['ĐỀ XUẤT HỌC TẬP'])
        for recommendation in report.report_data['recommendations']:
            writer.writerow([recommendation['title']])
            writer.writerow([recommendation['description']])
            writer.writerow([])

        # Thông tin cuối trang
        writer.writerow([f'Báo cáo được tạo lúc: {timezone.now().strftime("%H:%M %d/%m/%Y")}'])
        writer.writerow(['\u00a9 Learn Everything - Nền tảng học tập thông minh'])

        # Đặt con trỏ về đầu file
        output.seek(0)
        return output

    except Exception as e:
        logger.error(f"Lỗi khi tạo báo cáo CSV: {e}")
        return None

def generate_chart_image(chart_type, data, title=None, xlabel=None, ylabel=None):
    """
    Tạo hình ảnh biểu đồ và chuyển thành chuỗi base64.

    Args:
        chart_type: Loại biểu đồ ('bar', 'line', 'pie')
        data: Dữ liệu cho biểu đồ
        title: Tiêu đề biểu đồ
        xlabel: Nhãn trục x
        ylabel: Nhãn trục y

    Returns:
        str: Chuỗi base64 của hình ảnh biểu đồ
    """
    if not MATPLOTLIB_SUPPORT:
        return None

    try:
        # Tạo hình mới
        plt.figure(figsize=(8, 5))

        if chart_type == 'bar':
            # Biểu đồ cột
            labels = [item['label'] for item in data]
            values = [item['value'] for item in data]
            plt.bar(labels, values, color='#007bff')
            plt.xticks(rotation=45, ha='right')

        elif chart_type == 'line':
            # Biểu đồ đường
            labels = [item['label'] for item in data]
            values = [item['value'] for item in data]
            plt.plot(labels, values, marker='o', linestyle='-', color='#007bff')
            plt.xticks(rotation=45, ha='right')

        elif chart_type == 'pie':
            # Biểu đồ tròn
            labels = [item['label'] for item in data]
            values = [item['value'] for item in data]
            plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90,
                   colors=['#007bff', '#28a745', '#fd7e14', '#dc3545', '#6f42c1', '#17a2b8'])
            plt.axis('equal')  # Đảm bảo hình tròn

        # Thêm tiêu đề và nhãn trục
        if title:
            plt.title(title)
        if xlabel:
            plt.xlabel(xlabel)
        if ylabel:
            plt.ylabel(ylabel)

        # Điều chỉnh layout
        plt.tight_layout()

        # Lưu hình ảnh vào buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Chuyển hình ảnh thành chuỗi base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Đóng hình để giải phóng bộ nhớ
        plt.close()

        return image_base64

    except Exception as e:
        logger.error(f"Lỗi khi tạo biểu đồ: {e}")
        return None

def generate_pdf_report(report):
    """
    Tạo báo cáo dạng PDF.

    Args:
        report: Đối tượng AnalyticsReport

    Returns:
        BytesIO: Đối tượng BytesIO chứa nội dung PDF
    """
    try:
        # Tạo các biểu đồ nếu có hỗ trợ matplotlib
        charts = {}

        if MATPLOTLIB_SUPPORT:
            # Biểu đồ thời gian học tập theo ngày
            study_time_data = []
            for day in report.report_data['study_time']['study_time_by_day']:
                study_time_data.append({
                    'label': day['date'],
                    'value': day['study_time']
                })

            charts['study_time_chart'] = generate_chart_image(
                'bar',
                study_time_data,
                title='Thời gian học tập theo ngày',
                xlabel='Ngày',
                ylabel='Thời gian (giờ)'
            )

            # Biểu đồ phân bố thời gian theo chủ đề
            subject_distribution_data = []
            for subject in report.report_data['study_time']['study_time_by_subject']:
                subject_distribution_data.append({
                    'label': subject['subject_name'],
                    'value': subject['study_time']
                })

            charts['subject_distribution_chart'] = generate_chart_image(
                'pie',
                subject_distribution_data,
                title='Phân bố thời gian theo chủ đề'
            )

            # Biểu đồ điểm bài kiểm tra theo thời gian
            quiz_scores_data = []
            for day in report.report_data['quiz_performance']['quiz_scores_over_time']:
                quiz_scores_data.append({
                    'label': day['date'],
                    'value': day['score']
                })

            charts['quiz_scores_chart'] = generate_chart_image(
                'line',
                quiz_scores_data,
                title='Điểm bài kiểm tra theo thời gian',
                xlabel='Ngày',
                ylabel='Điểm (%)'
            )

        # Tạo template context
        context = {
            'report': report,
            'title': report.title,
            'description': report.description,
            'start_date': report.start_date,
            'end_date': report.end_date,
            'report_data': report.report_data,
            'generated_at': timezone.now(),
            'charts': charts,
            'has_charts': MATPLOTLIB_SUPPORT
        }

        # Lấy template
        template = get_template('learning_analytics/report_pdf.html')
        html = template.render(context)

        # Tạo file PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

        if not pdf.err:
            return result
        else:
            logger.error(f"Lỗi khi tạo PDF: {pdf.err}")
            return None

    except Exception as e:
        logger.error(f"Lỗi khi tạo báo cáo PDF: {e}")
        return None

def get_user_preferences(user):
    """
    Lấy tùy chọn phân tích của người dùng.

    Args:
        user: Đối tượng User

    Returns:
        AnalyticsPreference: Tùy chọn phân tích của người dùng
    """
    try:
        preferences, _ = AnalyticsPreference.objects.get_or_create(
            user=user,
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
        return preferences
    except Exception as e:
        logger.error(f"Lỗi khi lấy tùy chọn phân tích của người dùng: {e}")
        return None

def get_dashboard_data(user):
    """
    Lấy dữ liệu cho bảng điều khiển phân tích.

    Args:
        user: Đối tượng User

    Returns:
        dict: Dữ liệu cho bảng điều khiển
    """
    try:
        # Lấy tùy chọn phân tích của người dùng
        preferences = get_user_preferences(user)

        # Khởi tạo dữ liệu
        dashboard_data = {
            'preferences': preferences,
            'study_time': None,
            'quiz_performance': None,
            'flashcard_performance': None,
            'subject_distribution': None,
            'learning_patterns': None,
            'recommendations': None,
            'insights': None,
            'last_updated': timezone.now()
        }

        # Lấy dữ liệu theo tùy chọn của người dùng
        # Sử dụng tham số days cho tất cả các hàm để đảm bảo tính nhất quán
        days = 30  # Mặc định 30 ngày

        # Chỉ lấy dữ liệu cần thiết dựa trên tùy chọn của người dùng
        if preferences.show_study_time:
            dashboard_data['study_time'] = get_study_time_data(user, days)

        if preferences.show_quiz_performance:
            dashboard_data['quiz_performance'] = get_quiz_performance_data(user, days)

        if preferences.show_flashcard_performance:
            dashboard_data['flashcard_performance'] = get_flashcard_performance_data(user, days)

        if preferences.show_subject_distribution:
            dashboard_data['subject_distribution'] = get_subject_distribution_data(user, days)

        if preferences.show_learning_patterns:
            dashboard_data['learning_patterns'] = get_learning_patterns_data(user, days)

        if preferences.show_recommendations:
            dashboard_data['recommendations'] = get_recommendations(user, days)

        # Lấy các phân tích sâu (giới hạn số lượng để tăng hiệu suất)
        dashboard_data['insights'] = get_learning_insights(user, days)[:5]  # Chỉ lấy 5 phân tích đầu tiên

        return dashboard_data

    except Exception as e:
        logger.error(f"Lỗi khi lấy dữ liệu cho bảng điều khiển: {e}")
        return {
            'preferences': preferences,
            'error': str(e),
            'last_updated': timezone.now()
        }

def get_study_time_data(user, days=30):
    """
    Lấy dữ liệu thời gian học tập.

    Args:
        user: Đối tượng User
        days: Số ngày cần lấy dữ liệu (mặc định: 30 ngày)

    Returns:
        dict: Dữ liệu thời gian học tập
    """
    try:
        # Lấy ngày bắt đầu và ngày kết thúc
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=days)

        # Lấy các phiên học tập trong khoảng thời gian
        study_sessions = StudySession.objects.filter(
            user=user,
            start_time__date__gte=start_date,
            start_time__date__lte=end_date
        )

        # Tổng thời gian học tập (giờ)
        total_duration = study_sessions.aggregate(total=Sum('duration'))['total'] or 0
        total_study_time = round(total_duration / 60, 2)  # Chuyển từ phút sang giờ

        # Trung bình hàng ngày (giờ)
        if days > 0:
            daily_average = round(total_study_time / days, 2)
        else:
            daily_average = 0

        # Trung bình hàng tuần (giờ)
        weekly_average = round(daily_average * 7, 2)

        # Trung bình hàng tháng (giờ)
        monthly_average = round(daily_average * 30, 2)

        # Thời gian học tập theo ngày
        study_time_by_day = []
        current_date = start_date
        while current_date <= end_date:
            # Lấy các phiên học tập trong ngày
            daily_sessions = study_sessions.filter(
                start_time__date=current_date
            )

            # Tổng thời gian học tập trong ngày (giờ)
            daily_duration = daily_sessions.aggregate(total=Sum('duration'))['total'] or 0
            daily_study_time = round(daily_duration / 60, 2)  # Chuyển từ phút sang giờ

            # Thêm vào danh sách
            study_time_by_day.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day_of_week': current_date.strftime('%a'),
                'study_time': daily_study_time
            })

            # Chuyển sang ngày tiếp theo
            current_date += datetime.timedelta(days=1)

        # Thời gian học tập theo chủ đề
        study_time_by_subject = []
        subjects = Subject.objects.filter(
            topics__lessons__study_sessions__in=study_sessions
        ).distinct()

        for subject in subjects:
            # Lấy các phiên học tập theo chủ đề
            subject_sessions = study_sessions.filter(
                lesson__topic__subject=subject
            )

            # Tổng thời gian học tập theo chủ đề (giờ)
            subject_duration = subject_sessions.aggregate(total=Sum('duration'))['total'] or 0
            subject_study_time = round(subject_duration / 60, 2)  # Chuyển từ phút sang giờ

            # Tỷ lệ phần trăm
            if total_study_time > 0:
                percentage = round((subject_study_time / total_study_time) * 100, 2)
            else:
                percentage = 0

            # Thêm vào danh sách
            study_time_by_subject.append({
                'subject_id': subject.id,
                'subject_name': subject.name,
                'study_time': subject_study_time,
                'percentage': percentage
            })

        # Sắp xếp theo thời gian học tập giảm dần
        study_time_by_subject.sort(key=lambda x: x['study_time'], reverse=True)

        return {
            'total_study_time': total_study_time,
            'daily_average': daily_average,
            'weekly_average': weekly_average,
            'monthly_average': monthly_average,
            'study_time_by_day': study_time_by_day,
            'study_time_by_subject': study_time_by_subject
        }

    except Exception as e:
        logger.error(f"Lỗi khi lấy dữ liệu thời gian học tập: {e}")
        return {
            'total_study_time': 0,
            'daily_average': 0,
            'weekly_average': 0,
            'monthly_average': 0,
            'study_time_by_day': [],
            'study_time_by_subject': []
        }

def get_quiz_performance_data(user, days=30):
    """
    Lấy dữ liệu hiệu suất bài kiểm tra.

    Args:
        user: Đối tượng User
        days: Số ngày cần lấy dữ liệu (mặc định: 30 ngày)

    Returns:
        dict: Dữ liệu hiệu suất bài kiểm tra
    """
    try:
        # Lấy ngày bắt đầu và ngày kết thúc
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=days)

        # Lấy các lần làm bài kiểm tra trong khoảng thời gian
        quiz_attempts = QuizAttempt.objects.filter(
            user=user,
            completed_at__date__gte=start_date,
            completed_at__date__lte=end_date,
            is_completed=True
        )

        # Tổng số lần làm bài kiểm tra
        total_quizzes = quiz_attempts.count()

        # Tổng số câu hỏi
        total_questions = quiz_attempts.aggregate(total=Sum('total_questions'))['total'] or 0

        # Tổng số câu trả lời đúng
        correct_answers = quiz_attempts.aggregate(total=Sum('correct_answers'))['total'] or 0

        # Điểm trung bình
        if total_questions > 0:
            average_score = round((correct_answers / total_questions) * 100, 2)
        else:
            average_score = 0

        # Điểm theo chủ đề
        quiz_scores_by_subject = []
        subjects = Subject.objects.filter(
            topics__lessons__quizzes__attempts__in=quiz_attempts
        ).distinct()

        for subject in subjects:
            # Lấy các lần làm bài kiểm tra theo chủ đề
            subject_attempts = quiz_attempts.filter(
                quiz__lesson__topic__subject=subject
            )

            # Tổng số câu hỏi theo chủ đề
            subject_questions = subject_attempts.aggregate(total=Sum('total_questions'))['total'] or 0

            # Tổng số câu trả lời đúng theo chủ đề
            subject_correct = subject_attempts.aggregate(total=Sum('correct_answers'))['total'] or 0

            # Điểm theo chủ đề
            if subject_questions > 0:
                subject_score = round((subject_correct / subject_questions) * 100, 2)
            else:
                subject_score = 0

            # Thêm vào danh sách
            quiz_scores_by_subject.append({
                'subject_id': subject.id,
                'subject_name': subject.name,
                'score': subject_score,
                'total_quizzes': subject_attempts.count(),
                'total_questions': subject_questions,
                'correct_answers': subject_correct
            })

        # Sắp xếp theo điểm giảm dần
        quiz_scores_by_subject.sort(key=lambda x: x['score'], reverse=True)

        # Điểm theo thời gian
        quiz_scores_over_time = []
        current_date = start_date
        while current_date <= end_date:
            # Lấy các lần làm bài kiểm tra trong ngày
            daily_attempts = quiz_attempts.filter(
                completed_at__date=current_date
            )

            # Tổng số câu hỏi trong ngày
            daily_questions = daily_attempts.aggregate(total=Sum('total_questions'))['total'] or 0

            # Tổng số câu trả lời đúng trong ngày
            daily_correct = daily_attempts.aggregate(total=Sum('correct_answers'))['total'] or 0

            # Điểm trong ngày
            if daily_questions > 0:
                daily_score = round((daily_correct / daily_questions) * 100, 2)
            else:
                daily_score = 0

            # Thêm vào danh sách
            quiz_scores_over_time.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day_of_week': current_date.strftime('%a'),
                'score': daily_score,
                'total_quizzes': daily_attempts.count(),
                'total_questions': daily_questions,
                'correct_answers': daily_correct
            })

            # Chuyển sang ngày tiếp theo
            current_date += datetime.timedelta(days=1)

        return {
            'average_score': average_score,
            'total_quizzes': total_quizzes,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'quiz_scores_by_subject': quiz_scores_by_subject,
            'quiz_scores_over_time': quiz_scores_over_time
        }

    except Exception as e:
        logger.error(f"Lỗi khi lấy dữ liệu hiệu suất bài kiểm tra: {e}")
        return {
            'average_score': 0,
            'total_quizzes': 0,
            'total_questions': 0,
            'correct_answers': 0,
            'quiz_scores_by_subject': [],
            'quiz_scores_over_time': []
        }

def get_flashcard_performance_data(user, days=30):
    """
    Lấy dữ liệu hiệu suất flashcard.

    Args:
        user: Đối tượng User
        days: Số ngày cần lấy dữ liệu (mặc định: 30 ngày)

    Returns:
        dict: Dữ liệu hiệu suất flashcard
    """
    try:
        # Lấy ngày bắt đầu và ngày kết thúc
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=days)

        # Lấy các lịch ôn tập của người dùng
        schedules = SpacedRepetitionSchedule.objects.filter(
            user=user,
            updated_at__date__gte=start_date,
            updated_at__date__lte=end_date
        )

        # Tổng số thẻ
        total_cards = schedules.count()

        # Số thẻ đã thành thạo (recall_level = 3)
        mastered_cards = schedules.filter(recall_level=3).count()

        # Số thẻ đang học (recall_level = 2)
        learning_cards = schedules.filter(recall_level=2).count()

        # Số thẻ mới (recall_level = 1)
        new_cards = schedules.filter(recall_level=1).count()

        # Tỷ lệ ghi nhớ
        if total_cards > 0:
            retention_rate = round((mastered_cards / total_cards) * 100, 2)
        else:
            retention_rate = 0

        # Tỷ lệ ghi nhớ theo chủ đề
        retention_by_subject = []
        subjects = Subject.objects.filter(
            topics__lessons__flashcard_sets__flashcards__spaced_repetition_schedules__in=schedules
        ).distinct()

        for subject in subjects:
            # Lấy các lịch ôn tập theo chủ đề
            subject_schedules = schedules.filter(
                flashcard__flashcard_set__lesson__topic__subject=subject
            )

            # Tổng số thẻ theo chủ đề
            subject_total = subject_schedules.count()

            # Số thẻ đã thành thạo theo chủ đề
            subject_mastered = subject_schedules.filter(recall_level=3).count()

            # Tỷ lệ ghi nhớ theo chủ đề
            if subject_total > 0:
                subject_retention = round((subject_mastered / subject_total) * 100, 2)
            else:
                subject_retention = 0

            # Thêm vào danh sách
            retention_by_subject.append({
                'subject_id': subject.id,
                'subject_name': subject.name,
                'total_cards': subject_total,
                'mastered_cards': subject_mastered,
                'retention_rate': subject_retention
            })

        # Sắp xếp theo tỷ lệ ghi nhớ giảm dần
        retention_by_subject.sort(key=lambda x: x['retention_rate'], reverse=True)

        # Tỷ lệ ghi nhớ theo thời gian
        retention_over_time = []
        current_date = start_date
        while current_date <= end_date:
            # Lấy các lịch ôn tập được cập nhật trong ngày
            daily_schedules = schedules.filter(
                updated_at__date=current_date
            )

            # Tổng số thẻ được ôn tập trong ngày
            daily_total = daily_schedules.count()

            # Số thẻ đã thành thạo trong ngày
            daily_mastered = daily_schedules.filter(recall_level=3).count()

            # Số thẻ đang học trong ngày
            daily_learning = daily_schedules.filter(recall_level=2).count()

            # Số thẻ mới trong ngày
            daily_new = daily_schedules.filter(recall_level=1).count()

            # Tỷ lệ ghi nhớ trong ngày
            if daily_total > 0:
                daily_retention = round((daily_mastered / daily_total) * 100, 2)
            else:
                daily_retention = 0

            # Thêm vào danh sách
            retention_over_time.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day_of_week': current_date.strftime('%a'),
                'total_cards': daily_total,
                'mastered_cards': daily_mastered,
                'learning_cards': daily_learning,
                'new_cards': daily_new,
                'retention_rate': daily_retention
            })

            # Chuyển sang ngày tiếp theo
            current_date += datetime.timedelta(days=1)

        return {
            'total_cards': total_cards,
            'mastered_cards': mastered_cards,
            'learning_cards': learning_cards,
            'new_cards': new_cards,
            'retention_rate': retention_rate,
            'retention_by_subject': retention_by_subject,
            'retention_over_time': retention_over_time
        }

    except Exception as e:
        logger.error(f"Lỗi khi lấy dữ liệu hiệu suất flashcard: {e}")
        return {
            'total_cards': 0,
            'mastered_cards': 0,
            'learning_cards': 0,
            'new_cards': 0,
            'retention_rate': 0,
            'retention_by_subject': [],
            'retention_over_time': []
        }

def get_subject_distribution_data(user, days=30):
    """
    Lấy dữ liệu phân bố thời gian theo chủ đề.

    Args:
        user: Đối tượng User
        days: Số ngày cần lấy dữ liệu (mặc định: 30 ngày)

    Returns:
        dict: Dữ liệu phân bố thời gian theo chủ đề
    """
    try:
        # Lấy ngày bắt đầu và ngày kết thúc
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=days)

        # Lấy tất cả các chủ đề mà người dùng đã học
        subjects = Subject.objects.filter(
            topics__lessons__study_sessions__user=user,
            topics__lessons__study_sessions__start_time__date__gte=start_date,
            topics__lessons__study_sessions__start_time__date__lte=end_date
        ).distinct()

        # Danh sách chủ đề
        subject_list = []
        for subject in subjects:
            subject_list.append({
                'id': subject.id,
                'name': subject.name,
                'description': subject.description
            })

        # Lấy dữ liệu thời gian học tập theo chủ đề
        study_time_data = get_study_time_data(user, days)
        study_time_by_subject = study_time_data['study_time_by_subject']

        # Lấy dữ liệu bài kiểm tra theo chủ đề
        quiz_performance_data = get_quiz_performance_data(user, days)
        quiz_attempts_by_subject = quiz_performance_data['quiz_scores_by_subject']

        # Lấy dữ liệu flashcard theo chủ đề
        flashcard_performance_data = get_flashcard_performance_data(user, days)
        flashcard_reviews_by_subject = flashcard_performance_data['retention_by_subject']

        # Tổng hợp dữ liệu
        combined_data = []
        for subject in subjects:
            # Tìm dữ liệu thời gian học tập
            study_time_item = next((item for item in study_time_by_subject if item['subject_id'] == subject.id), None)
            study_time = study_time_item['study_time'] if study_time_item else 0
            study_time_percentage = study_time_item['percentage'] if study_time_item else 0

            # Tìm dữ liệu bài kiểm tra
            quiz_item = next((item for item in quiz_attempts_by_subject if item['subject_id'] == subject.id), None)
            quiz_score = quiz_item['score'] if quiz_item else 0
            quiz_count = quiz_item['total_quizzes'] if quiz_item else 0

            # Tìm dữ liệu flashcard
            flashcard_item = next((item for item in flashcard_reviews_by_subject if item['subject_id'] == subject.id), None)
            flashcard_retention = flashcard_item['retention_rate'] if flashcard_item else 0
            flashcard_count = flashcard_item['total_cards'] if flashcard_item else 0

            # Tính điểm tổng hợp
            # 50% thời gian học tập, 30% điểm bài kiểm tra, 20% tỷ lệ ghi nhớ flashcard
            composite_score = (study_time_percentage * 0.5) + (quiz_score * 0.3) + (flashcard_retention * 0.2)

            # Thêm vào danh sách
            combined_data.append({
                'subject_id': subject.id,
                'subject_name': subject.name,
                'study_time': study_time,
                'study_time_percentage': study_time_percentage,
                'quiz_score': quiz_score,
                'quiz_count': quiz_count,
                'flashcard_retention': flashcard_retention,
                'flashcard_count': flashcard_count,
                'composite_score': round(composite_score, 2)
            })

        # Sắp xếp theo điểm tổng hợp giảm dần
        combined_data.sort(key=lambda x: x['composite_score'], reverse=True)

        return {
            'subjects': subject_list,
            'study_time_by_subject': study_time_by_subject,
            'quiz_attempts_by_subject': quiz_attempts_by_subject,
            'flashcard_reviews_by_subject': flashcard_reviews_by_subject,
            'combined_data': combined_data
        }

    except Exception as e:
        logger.error(f"Lỗi khi lấy dữ liệu phân bố thời gian theo chủ đề: {e}")
        return {
            'subjects': [],
            'study_time_by_subject': [],
            'quiz_attempts_by_subject': [],
            'flashcard_reviews_by_subject': [],
            'combined_data': []
        }

def get_learning_patterns_data(user, days=30):
    """
    Lấy dữ liệu mẫu học tập.

    Args:
        user: Đối tượng User
        days: Số ngày cần lấy dữ liệu (mặc định: 30 ngày)

    Returns:
        dict: Dữ liệu mẫu học tập
    """
    try:
        # Lấy ngày bắt đầu và ngày kết thúc
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=days)

        # Lấy các phiên học tập trong khoảng thời gian
        study_sessions = StudySession.objects.filter(
            user=user,
            start_time__date__gte=start_date,
            start_time__date__lte=end_date
        )

        # Thời gian học tập theo giờ trong ngày
        study_time_by_hour = [0] * 24  # 24 giờ trong ngày

        for session in study_sessions:
            # Lấy giờ bắt đầu
            start_hour = session.start_time.hour

            # Tính thời gian học tập (giờ)
            duration_hours = session.duration / 60  # Chuyển từ phút sang giờ

            # Cộng vào giờ tương ứng
            study_time_by_hour[start_hour] += duration_hours

        # Làm tròn thời gian học tập theo giờ
        study_time_by_hour = [round(time, 2) for time in study_time_by_hour]

        # Thời gian học tập theo ngày trong tuần
        study_time_by_day_of_week = [0] * 7  # 7 ngày trong tuần

        for session in study_sessions:
            # Lấy ngày trong tuần (0 = Thứ 2, 6 = Chủ nhật)
            day_of_week = session.start_time.weekday()

            # Tính thời gian học tập (giờ)
            duration_hours = session.duration / 60  # Chuyển từ phút sang giờ

            # Cộng vào ngày tương ứng
            study_time_by_day_of_week[day_of_week] += duration_hours

        # Làm tròn thời gian học tập theo ngày trong tuần
        study_time_by_day_of_week = [round(time, 2) for time in study_time_by_day_of_week]

        # Thời gian học tập theo tháng
        study_time_by_month = [0] * 12  # 12 tháng trong năm

        for session in study_sessions:
            # Lấy tháng (1-12)
            month = session.start_time.month - 1  # Chuyển sang index 0-11

            # Tính thời gian học tập (giờ)
            duration_hours = session.duration / 60  # Chuyển từ phút sang giờ

            # Cộng vào tháng tương ứng
            study_time_by_month[month] += duration_hours

        # Làm tròn thời gian học tập theo tháng
        study_time_by_month = [round(time, 2) for time in study_time_by_month]

        # Tính điểm độ đều (consistency score)
        # Dựa trên số ngày học tập trong khoảng thời gian
        study_days = study_sessions.values('start_time__date').distinct().count()
        consistency_score = round((study_days / days) * 100, 2) if days > 0 else 0

        # Tính điểm tập trung (focus score)
        # Dựa trên thời gian trung bình của mỗi phiên học tập
        total_sessions = study_sessions.count()
        total_duration = study_sessions.aggregate(total=Sum('duration'))['total'] or 0

        if total_sessions > 0:
            avg_session_duration = total_duration / total_sessions
            # Điểm tập trung dựa trên thời gian trung bình của mỗi phiên học tập
            # Giả sử phiên học tập lý tưởng là 25-45 phút (kỹ thuật Pomodoro)
            if avg_session_duration < 15:  # Quá ngắn
                focus_score = round((avg_session_duration / 25) * 100, 2)
            elif avg_session_duration > 60:  # Quá dài
                focus_score = round((60 / avg_session_duration) * 100, 2)
            else:  # Lý tưởng
                focus_score = 100
        else:
            focus_score = 0

        # Giới hạn điểm tập trung trong khoảng 0-100
        focus_score = max(0, min(100, focus_score))

        # Chuẩn bị dữ liệu theo định dạng phù hợp cho biểu đồ
        formatted_study_time_by_hour = [
            {'hour': hour, 'study_time': study_time_by_hour[hour]}
            for hour in range(24)
        ]

        day_names = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
        formatted_study_time_by_day_of_week = [
            {'day': day_names[day], 'study_time': study_time_by_day_of_week[day]}
            for day in range(7)
        ]

        month_names = ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6',
                      'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12']
        formatted_study_time_by_month = [
            {'month': month_names[month], 'study_time': study_time_by_month[month]}
            for month in range(12)
        ]

        # Phân tích thói quen học tập
        peak_hour = study_time_by_hour.index(max(study_time_by_hour)) if max(study_time_by_hour) > 0 else None
        peak_day = study_time_by_day_of_week.index(max(study_time_by_day_of_week)) if max(study_time_by_day_of_week) > 0 else None

        habits = []

        if peak_hour is not None:
            if 5 <= peak_hour <= 11:
                habits.append("Bạn có xu hướng học tập vào buổi sáng.")
            elif 12 <= peak_hour <= 17:
                habits.append("Bạn có xu hướng học tập vào buổi chiều.")
            else:
                habits.append("Bạn có xu hướng học tập vào buổi tối.")

        if peak_day is not None:
            if peak_day < 5:  # Thứ 2 - Thứ 6
                habits.append(f"Bạn học tập nhiều nhất vào {day_names[peak_day]}.")
            else:  # Thứ 7 - Chủ nhật
                habits.append(f"Bạn có xu hướng học tập vào cuối tuần, đặc biệt là {day_names[peak_day]}.")

        if consistency_score >= 80:
            habits.append("Bạn có tính đều đặn cao trong học tập.")
        elif consistency_score >= 50:
            habits.append("Bạn có tính đều đặn trung bình trong học tập.")
        else:
            habits.append("Bạn cần cải thiện tính đều đặn trong học tập.")

        if focus_score >= 80:
            habits.append("Bạn có khả năng tập trung cao khi học tập.")
        elif focus_score >= 50:
            habits.append("Bạn có khả năng tập trung trung bình khi học tập.")
        else:
            habits.append("Bạn cần cải thiện khả năng tập trung khi học tập.")

        return {
            'study_time_by_hour': formatted_study_time_by_hour,
            'study_time_by_day_of_week': formatted_study_time_by_day_of_week,
            'study_time_by_month': formatted_study_time_by_month,
            'consistency_score': consistency_score,
            'focus_score': focus_score,
            'habits': habits,
            'peak_hour': peak_hour,
            'peak_day': peak_day
        }

    except Exception as e:
        logger.error(f"Lỗi khi lấy dữ liệu mẫu học tập: {e}")
        return {
            'study_time_by_hour': [],
            'study_time_by_day_of_week': [],
            'study_time_by_month': [],
            'consistency_score': 0,
            'focus_score': 0,
            'habits': [],
            'peak_hour': None,
            'peak_day': None
        }

def get_weaknesses(user, days=30):
    """
    Phát hiện điểm yếu trong học tập của người dùng.

    Args:
        user: Đối tượng User
        days: Số ngày cần lấy dữ liệu (mặc định: 30 ngày)

    Returns:
        list: Danh sách điểm yếu
    """
    try:
        weaknesses = []

        # Lấy dữ liệu phân bố thời gian theo chủ đề
        subject_distribution = get_subject_distribution_data(user, days)
        combined_data = subject_distribution.get('combined_data', [])

        # Lấy dữ liệu hiệu suất bài kiểm tra
        quiz_performance = get_quiz_performance_data(user, days)
        quiz_scores_by_subject = quiz_performance.get('quiz_scores_by_subject', [])

        # Lấy dữ liệu hiệu suất flashcard
        flashcard_performance = get_flashcard_performance_data(user, days)
        retention_by_subject = flashcard_performance.get('retention_by_subject', [])

        # Lấy dữ liệu mẫu học tập
        learning_patterns = get_learning_patterns_data(user, days)
        consistency_score = learning_patterns.get('consistency_score', 0)
        focus_score = learning_patterns.get('focus_score', 0)

        # Phát hiện điểm yếu về chủ đề
        if combined_data:
            # Lấy 3 chủ đề có điểm tổng hợp thấp nhất
            bottom_subjects = sorted(combined_data, key=lambda x: x['composite_score'])[:3]

            for subject in bottom_subjects:
                if subject['composite_score'] < 50:  # Ngưỡng điểm yếu
                    weaknesses.append({
                        'insight_type': 'weakness',
                        'title': f"Bạn cần cải thiện chủ đề {subject['subject_name']}",
                        'description': f"Hiệu suất của bạn trong chủ đề {subject['subject_name']} chỉ đạt {subject['composite_score']}%. Hãy dành thêm thời gian để cải thiện.",
                        'data_points': subject,
                        'subject_id': subject['subject_id'],
                        'subject_name': subject['subject_name'],
                        'is_highlighted': subject['composite_score'] < 30
                    })

        # Phát hiện điểm yếu về bài kiểm tra
        if quiz_scores_by_subject:
            # Lấy các chủ đề có điểm bài kiểm tra thấp
            for subject in quiz_scores_by_subject:
                if subject['score'] < 60 and subject['total_quizzes'] >= 2:  # Ngưỡng điểm yếu và ít nhất 2 bài kiểm tra
                    weaknesses.append({
                        'insight_type': 'weakness',
                        'title': f"Bạn cần cải thiện điểm bài kiểm tra trong chủ đề {subject['subject_name']}",
                        'description': f"Bạn chỉ đạt điểm trung bình {subject['score']}% trong {subject['total_quizzes']} bài kiểm tra của chủ đề {subject['subject_name']}. Hãy ôn tập lại kiến thức và làm thêm bài kiểm tra.",
                        'data_points': subject,
                        'subject_id': subject['subject_id'],
                        'subject_name': subject['subject_name'],
                        'is_highlighted': subject['score'] < 40
                    })

        # Phát hiện điểm yếu về flashcard
        if retention_by_subject:
            # Lấy các chủ đề có tỷ lệ ghi nhớ thấp
            for subject in retention_by_subject:
                if subject['retention_rate'] < 50 and subject['total_cards'] >= 10:  # Ngưỡng tỷ lệ ghi nhớ yếu và ít nhất 10 thẻ
                    weaknesses.append({
                        'insight_type': 'weakness',
                        'title': f"Bạn cần cải thiện việc ghi nhớ thẻ trong chủ đề {subject['subject_name']}",
                        'description': f"Bạn chỉ có tỷ lệ ghi nhớ {subject['retention_rate']}% với {subject['total_cards']} thẻ trong chủ đề {subject['subject_name']}. Hãy ôn tập thường xuyên hơn.",
                        'data_points': subject,
                        'subject_id': subject['subject_id'],
                        'subject_name': subject['subject_name'],
                        'is_highlighted': subject['retention_rate'] < 30
                    })

        # Phát hiện điểm yếu về tính đều đặn
        if consistency_score < 50:  # Ngưỡng tính đều đặn yếu
            weaknesses.append({
                'insight_type': 'weakness',
                'title': "Bạn cần cải thiện tính đều đặn trong học tập",
                'description': f"Tính đều đặn trong học tập của bạn chỉ đạt {consistency_score}%. Hãy cố gắng học tập đều đặn hơn để tăng hiệu quả.",
                'data_points': {'consistency_score': consistency_score},
                'subject_id': None,
                'subject_name': None,
                'is_highlighted': consistency_score < 30
            })

        # Phát hiện điểm yếu về khả năng tập trung
        if focus_score < 50:  # Ngưỡng khả năng tập trung yếu
            weaknesses.append({
                'insight_type': 'weakness',
                'title': "Bạn cần cải thiện khả năng tập trung khi học tập",
                'description': f"Điểm tập trung của bạn chỉ đạt {focus_score}%. Hãy thử kỹ thuật Pomodoro hoặc các phương pháp tăng khả năng tập trung khác.",
                'data_points': {'focus_score': focus_score},
                'subject_id': None,
                'subject_name': None,
                'is_highlighted': focus_score < 30
            })

        return weaknesses

    except Exception as e:
        logger.error(f"Lỗi khi phát hiện điểm yếu: {e}")
        return []

def get_learning_patterns(user, days=30):
    """
    Phát hiện mẫu học tập của người dùng.

    Args:
        user: Đối tượng User
        days: Số ngày cần lấy dữ liệu (mặc định: 30 ngày)

    Returns:
        list: Danh sách mẫu học tập
    """
    try:
        patterns = []

        # Lấy dữ liệu mẫu học tập
        learning_patterns_data = get_learning_patterns_data(user, days)

        # Lấy các thói quen học tập
        habits = learning_patterns_data.get('habits', [])
        peak_hour = learning_patterns_data.get('peak_hour')
        peak_day = learning_patterns_data.get('peak_day')
        study_time_by_hour = learning_patterns_data.get('study_time_by_hour', [])
        study_time_by_day_of_week = learning_patterns_data.get('study_time_by_day_of_week', [])

        # Phát hiện mẫu học tập theo giờ trong ngày
        if peak_hour is not None:
            # Chuyển giờ sang dạng 12 giờ
            hour_12 = peak_hour if peak_hour <= 12 else peak_hour - 12
            am_pm = 'AM' if peak_hour < 12 else 'PM'

            # Phân loại thời gian trong ngày
            if 5 <= peak_hour <= 11:
                time_of_day = 'buổi sáng'
            elif 12 <= peak_hour <= 17:
                time_of_day = 'buổi chiều'
            else:
                time_of_day = 'buổi tối'

            patterns.append({
                'insight_type': 'pattern',
                'title': f"Bạn thường học tập vào {time_of_day}",
                'description': f"Bạn học tập nhiều nhất vào lúc {hour_12} {am_pm}. Việc hiểu rõ thời điểm học tập hiệu quả nhất giúp bạn lên kế hoạch học tập tốt hơn.",
                'data_points': {'peak_hour': peak_hour, 'study_time_by_hour': study_time_by_hour},
                'subject_id': None,
                'subject_name': None,
                'is_highlighted': False
            })

        # Phát hiện mẫu học tập theo ngày trong tuần
        if peak_day is not None:
            day_names = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
            peak_day_name = day_names[peak_day]

            # Phân loại ngày trong tuần
            if peak_day < 5:  # Thứ 2 - Thứ 6
                day_category = 'ngày trong tuần'
            else:  # Thứ 7 - Chủ nhật
                day_category = 'cuối tuần'

            patterns.append({
                'insight_type': 'pattern',
                'title': f"Bạn thường học tập vào {peak_day_name}",
                'description': f"Bạn học tập nhiều nhất vào {peak_day_name} ({day_category}). Việc hiểu rõ ngày học tập hiệu quả nhất giúp bạn lên kế hoạch học tập tốt hơn.",
                'data_points': {'peak_day': peak_day, 'study_time_by_day_of_week': study_time_by_day_of_week},
                'subject_id': None,
                'subject_name': None,
                'is_highlighted': False
            })

        # Phát hiện mẫu học tập theo thói quen
        for habit in habits:
            patterns.append({
                'insight_type': 'pattern',
                'title': habit,
                'description': f"{habit} Việc hiểu rõ thói quen học tập giúp bạn cải thiện hiệu quả học tập.",
                'data_points': {'habits': habits},
                'subject_id': None,
                'subject_name': None,
                'is_highlighted': False
            })

        return patterns

    except Exception as e:
        logger.error(f"Lỗi khi phát hiện mẫu học tập: {e}")
        return []

def get_improvements(user, days=30):
    """
    Phát hiện cải thiện trong học tập của người dùng.

    Args:
        user: Đối tượng User
        days: Số ngày cần lấy dữ liệu (mặc định: 30 ngày)

    Returns:
        list: Danh sách cải thiện
    """
    try:
        improvements = []

        # Lấy ngày bắt đầu và ngày kết thúc
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=days)
        mid_date = start_date + datetime.timedelta(days=days // 2)

        # Lấy dữ liệu hiệu suất bài kiểm tra
        quiz_attempts_first_half = QuizAttempt.objects.filter(
            user=user,
            completed_at__date__gte=start_date,
            completed_at__date__lt=mid_date,
            is_completed=True
        )

        quiz_attempts_second_half = QuizAttempt.objects.filter(
            user=user,
            completed_at__date__gte=mid_date,
            completed_at__date__lte=end_date,
            is_completed=True
        )

        # Tính điểm trung bình của nửa đầu và nửa sau
        first_half_total_questions = quiz_attempts_first_half.aggregate(total=Sum('total_questions'))['total'] or 0
        first_half_correct_answers = quiz_attempts_first_half.aggregate(total=Sum('correct_answers'))['total'] or 0

        second_half_total_questions = quiz_attempts_second_half.aggregate(total=Sum('total_questions'))['total'] or 0
        second_half_correct_answers = quiz_attempts_second_half.aggregate(total=Sum('correct_answers'))['total'] or 0

        first_half_score = (first_half_correct_answers / first_half_total_questions * 100) if first_half_total_questions > 0 else 0
        second_half_score = (second_half_correct_answers / second_half_total_questions * 100) if second_half_total_questions > 0 else 0

        # Phát hiện cải thiện về điểm bài kiểm tra
        if first_half_total_questions > 0 and second_half_total_questions > 0:
            score_improvement = second_half_score - first_half_score
            if score_improvement >= 10:  # Cải thiện ít nhất 10%
                improvements.append({
                    'insight_type': 'improvement',
                    'title': "Bạn đã cải thiện điểm bài kiểm tra",
                    'description': f"Bạn đã cải thiện điểm bài kiểm tra từ {first_half_score:.1f}% lên {second_half_score:.1f}%, tăng {score_improvement:.1f}%. Tiếp tục phát huy!",
                    'data_points': {
                        'first_half_score': first_half_score,
                        'second_half_score': second_half_score,
                        'improvement': score_improvement
                    },
                    'subject_id': None,
                    'subject_name': None,
                    'is_highlighted': score_improvement >= 20  # Cải thiện ít nhất 20% sẽ được nổi bật
                })

        # Lấy dữ liệu hiệu suất flashcard
        schedules_first_half = SpacedRepetitionSchedule.objects.filter(
            user=user,
            updated_at__date__gte=start_date,
            updated_at__date__lt=mid_date
        )

        schedules_second_half = SpacedRepetitionSchedule.objects.filter(
            user=user,
            updated_at__date__gte=mid_date,
            updated_at__date__lte=end_date
        )

        # Tính tỷ lệ ghi nhớ của nửa đầu và nửa sau
        first_half_total_cards = schedules_first_half.count()
        first_half_mastered_cards = schedules_first_half.filter(recall_level=3).count()

        second_half_total_cards = schedules_second_half.count()
        second_half_mastered_cards = schedules_second_half.filter(recall_level=3).count()

        first_half_retention = (first_half_mastered_cards / first_half_total_cards * 100) if first_half_total_cards > 0 else 0
        second_half_retention = (second_half_mastered_cards / second_half_total_cards * 100) if second_half_total_cards > 0 else 0

        # Phát hiện cải thiện về tỷ lệ ghi nhớ flashcard
        if first_half_total_cards > 0 and second_half_total_cards > 0:
            retention_improvement = second_half_retention - first_half_retention
            if retention_improvement >= 10:  # Cải thiện ít nhất 10%
                improvements.append({
                    'insight_type': 'improvement',
                    'title': "Bạn đã cải thiện tỷ lệ ghi nhớ flashcard",
                    'description': f"Bạn đã cải thiện tỷ lệ ghi nhớ flashcard từ {first_half_retention:.1f}% lên {second_half_retention:.1f}%, tăng {retention_improvement:.1f}%. Tiếp tục ôn tập đều đặn!",
                    'data_points': {
                        'first_half_retention': first_half_retention,
                        'second_half_retention': second_half_retention,
                        'improvement': retention_improvement
                    },
                    'subject_id': None,
                    'subject_name': None,
                    'is_highlighted': retention_improvement >= 20  # Cải thiện ít nhất 20% sẽ được nổi bật
                })

        # Lấy dữ liệu thời gian học tập
        sessions_first_half = StudySession.objects.filter(
            user=user,
            start_time__date__gte=start_date,
            start_time__date__lt=mid_date
        )

        sessions_second_half = StudySession.objects.filter(
            user=user,
            start_time__date__gte=mid_date,
            start_time__date__lte=end_date
        )

        # Tính tổng thời gian học tập của nửa đầu và nửa sau
        first_half_duration = sessions_first_half.aggregate(total=Sum('duration'))['total'] or 0
        second_half_duration = sessions_second_half.aggregate(total=Sum('duration'))['total'] or 0

        # Phát hiện cải thiện về thời gian học tập
        if first_half_duration > 0:
            duration_improvement_percentage = ((second_half_duration - first_half_duration) / first_half_duration * 100)
            if duration_improvement_percentage >= 20:  # Cải thiện ít nhất 20%
                improvements.append({
                    'insight_type': 'improvement',
                    'title': "Bạn đã tăng thời gian học tập",
                    'description': f"Bạn đã tăng thời gian học tập từ {first_half_duration} phút lên {second_half_duration} phút, tăng {duration_improvement_percentage:.1f}%. Tiếp tục duy trì thói quen học tập tốt!",
                    'data_points': {
                        'first_half_duration': first_half_duration,
                        'second_half_duration': second_half_duration,
                        'improvement_percentage': duration_improvement_percentage
                    },
                    'subject_id': None,
                    'subject_name': None,
                    'is_highlighted': duration_improvement_percentage >= 50  # Cải thiện ít nhất 50% sẽ được nổi bật
                })

        # Tính số ngày học tập của nửa đầu và nửa sau
        first_half_study_days = sessions_first_half.values('start_time__date').distinct().count()
        second_half_study_days = sessions_second_half.values('start_time__date').distinct().count()

        # Phát hiện cải thiện về tính đều đặn
        half_days = days // 2
        if half_days > 0:
            first_half_consistency = (first_half_study_days / half_days * 100)
            second_half_consistency = (second_half_study_days / half_days * 100)

            consistency_improvement = second_half_consistency - first_half_consistency
            if consistency_improvement >= 15:  # Cải thiện ít nhất 15%
                improvements.append({
                    'insight_type': 'improvement',
                    'title': "Bạn đã cải thiện tính đều đặn trong học tập",
                    'description': f"Bạn đã cải thiện tính đều đặn trong học tập từ {first_half_consistency:.1f}% lên {second_half_consistency:.1f}%, tăng {consistency_improvement:.1f}%. Học tập đều đặn giúp tăng hiệu quả học tập!",
                    'data_points': {
                        'first_half_consistency': first_half_consistency,
                        'second_half_consistency': second_half_consistency,
                        'improvement': consistency_improvement
                    },
                    'subject_id': None,
                    'subject_name': None,
                    'is_highlighted': consistency_improvement >= 30  # Cải thiện ít nhất 30% sẽ được nổi bật
                })

        return improvements

    except Exception as e:
        logger.error(f"Lỗi khi phát hiện cải thiện: {e}")
        return []

def get_milestones(user, days=30):
    """
    Phát hiện cột mốc trong học tập của người dùng.

    Args:
        user: Đối tượng User
        days: Số ngày cần lấy dữ liệu (mặc định: 30 ngày)

    Returns:
        list: Danh sách cột mốc
    """
    try:
        milestones = []

        # Lấy ngày bắt đầu và ngày kết thúc
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=days)

        # Lấy dữ liệu tổng thời gian học tập
        study_sessions = StudySession.objects.filter(user=user, start_time__date__gte=start_date, start_time__date__lte=end_date)
        total_duration = study_sessions.aggregate(total=Sum('duration'))['total'] or 0
        total_study_time_hours = total_duration / 60  # Chuyển từ phút sang giờ

        # Lấy dữ liệu tổng số bài kiểm tra
        quiz_attempts = QuizAttempt.objects.filter(user=user, is_completed=True, completed_at__date__gte=start_date, completed_at__date__lte=end_date)
        total_quizzes = quiz_attempts.count()

        # Lấy dữ liệu tổng số flashcard
        schedules = SpacedRepetitionSchedule.objects.filter(user=user, updated_at__date__gte=start_date, updated_at__date__lte=end_date)
        total_cards = schedules.count()
        mastered_cards = schedules.filter(recall_level=3).count()

        # Cột mốc về thời gian học tập
        study_time_milestones = [
            {'threshold': 10, 'title': "10 giờ học tập", 'description': "Bạn đã hoàn thành 10 giờ học tập trên nền tảng. Tiếp tục phát huy!"},
            {'threshold': 50, 'title': "50 giờ học tập", 'description': "Bạn đã hoàn thành 50 giờ học tập trên nền tảng. Đây là một thành tựu đáng kể!"},
            {'threshold': 100, 'title': "100 giờ học tập", 'description': "Bạn đã hoàn thành 100 giờ học tập trên nền tảng. Bạn đã đầu tư rất nhiều thời gian cho việc học tập!"},
            {'threshold': 500, 'title': "500 giờ học tập", 'description': "Bạn đã hoàn thành 500 giờ học tập trên nền tảng. Bạn đã trở thành một học viên chuyên nghiệp!"},
            {'threshold': 1000, 'title': "1000 giờ học tập", 'description': "Bạn đã hoàn thành 1000 giờ học tập trên nền tảng. Bạn đã đạt đến cấp độ thành thạo!"}
        ]

        for milestone in study_time_milestones:
            if total_study_time_hours >= milestone['threshold']:
                milestones.append({
                    'insight_type': 'milestone',
                    'title': milestone['title'],
                    'description': milestone['description'],
                    'data_points': {'total_study_time_hours': total_study_time_hours},
                    'subject_id': None,
                    'subject_name': None,
                    'is_highlighted': milestone['threshold'] >= 100
                })

        # Cột mốc về số lượng bài kiểm tra
        quiz_milestones = [
            {'threshold': 10, 'title': "10 bài kiểm tra", 'description': "Bạn đã hoàn thành 10 bài kiểm tra. Tiếp tục kiểm tra kiến thức của bạn!"},
            {'threshold': 50, 'title': "50 bài kiểm tra", 'description': "Bạn đã hoàn thành 50 bài kiểm tra. Bạn đang xây dựng một thói quen kiểm tra kiến thức tốt!"},
            {'threshold': 100, 'title': "100 bài kiểm tra", 'description': "Bạn đã hoàn thành 100 bài kiểm tra. Đây là một thành tựu đáng kể!"},
            {'threshold': 500, 'title': "500 bài kiểm tra", 'description': "Bạn đã hoàn thành 500 bài kiểm tra. Bạn đã trở thành một chuyên gia kiểm tra kiến thức!"}
        ]

        for milestone in quiz_milestones:
            if total_quizzes >= milestone['threshold']:
                milestones.append({
                    'insight_type': 'milestone',
                    'title': milestone['title'],
                    'description': milestone['description'],
                    'data_points': {'total_quizzes': total_quizzes},
                    'subject_id': None,
                    'subject_name': None,
                    'is_highlighted': milestone['threshold'] >= 100
                })

        # Cột mốc về số lượng flashcard
        card_milestones = [
            {'threshold': 50, 'title': "50 thẻ ghi nhớ", 'description': "Bạn đã học 50 thẻ ghi nhớ. Tiếp tục mở rộng bộ sưu tập của bạn!"},
            {'threshold': 100, 'title': "100 thẻ ghi nhớ", 'description': "Bạn đã học 100 thẻ ghi nhớ. Bạn đang xây dựng một bộ sưu tập ấn tượng!"},
            {'threshold': 500, 'title': "500 thẻ ghi nhớ", 'description': "Bạn đã học 500 thẻ ghi nhớ. Đây là một thành tựu đáng kể!"},
            {'threshold': 1000, 'title': "1000 thẻ ghi nhớ", 'description': "Bạn đã học 1000 thẻ ghi nhớ. Bạn đã trở thành một chuyên gia ghi nhớ!"}
        ]

        for milestone in card_milestones:
            if total_cards >= milestone['threshold']:
                milestones.append({
                    'insight_type': 'milestone',
                    'title': milestone['title'],
                    'description': milestone['description'],
                    'data_points': {'total_cards': total_cards},
                    'subject_id': None,
                    'subject_name': None,
                    'is_highlighted': milestone['threshold'] >= 500
                })

        # Cột mốc về số lượng thẻ đã thành thạo
        mastered_milestones = [
            {'threshold': 25, 'title': "25 thẻ đã thành thạo", 'description': "Bạn đã thành thạo 25 thẻ ghi nhớ. Tiếp tục ôn tập để thành thạo thêm nhiều thẻ!"},
            {'threshold': 50, 'title': "50 thẻ đã thành thạo", 'description': "Bạn đã thành thạo 50 thẻ ghi nhớ. Bạn đang xây dựng một kho kiến thức vững chắc!"},
            {'threshold': 100, 'title': "100 thẻ đã thành thạo", 'description': "Bạn đã thành thạo 100 thẻ ghi nhớ. Đây là một thành tựu đáng kể!"},
            {'threshold': 500, 'title': "500 thẻ đã thành thạo", 'description': "Bạn đã thành thạo 500 thẻ ghi nhớ. Bạn đã trở thành một chuyên gia ghi nhớ!"}
        ]

        for milestone in mastered_milestones:
            if mastered_cards >= milestone['threshold']:
                milestones.append({
                    'insight_type': 'milestone',
                    'title': milestone['title'],
                    'description': milestone['description'],
                    'data_points': {'mastered_cards': mastered_cards, 'total_cards': total_cards},
                    'subject_id': None,
                    'subject_name': None,
                    'is_highlighted': milestone['threshold'] >= 100
                })

        # Sắp xếp các cột mốc theo ngưỡng giảm dần
        milestones.sort(key=lambda x: x['data_points'].get('total_study_time_hours', 0) +
                              x['data_points'].get('total_quizzes', 0) +
                              x['data_points'].get('total_cards', 0) +
                              x['data_points'].get('mastered_cards', 0),
                      reverse=True)

        return milestones

    except Exception as e:
        logger.error(f"Lỗi khi phát hiện cột mốc: {e}")
        return []

def get_recommendations(user, days=30):
    """
    Lấy đề xuất học tập.

    Args:
        user: Đối tượng User
        days: Số ngày cần lấy dữ liệu (mặc định: 30 ngày)

    Returns:
        list: Danh sách đề xuất học tập
    """
    try:
        recommendations = []

        # Lấy dữ liệu phân tích sâu
        insights = get_learning_insights(user, days)

        # Lấy điểm yếu
        weaknesses = [insight for insight in insights if insight['insight_type'] == 'weakness']

        # Lấy dữ liệu phân bố thời gian theo chủ đề
        subject_distribution = get_subject_distribution_data(user, days)
        combined_data = subject_distribution.get('combined_data', [])

        # Lấy dữ liệu mẫu học tập
        learning_patterns = get_learning_patterns_data(user, days)
        consistency_score = learning_patterns.get('consistency_score', 0)
        focus_score = learning_patterns.get('focus_score', 0)

        # Đề xuất chủ đề dựa trên điểm yếu
        for weakness in weaknesses:
            if 'subject_id' in weakness and weakness['subject_id'] is not None:
                subject_id = weakness['subject_id']
                subject_name = weakness['subject_name']

                # Tìm các bài học trong chủ đề
                lessons = Lesson.objects.filter(topic__subject_id=subject_id).order_by('topic__order', 'order')[:5]

                if lessons.exists():
                    # Đề xuất bài học
                    for lesson in lessons:
                        recommendations.append({
                            'recommendation_type': 'lesson',
                            'title': f"Học bài {lesson.name}",
                            'description': f"Bạn cần cải thiện hiệu suất trong chủ đề {subject_name}. Hãy học bài {lesson.name} để cải thiện kiến thức của bạn.",
                            'priority': 'high',
                            'subject_id': subject_id,
                            'subject_name': subject_name,
                            'topic_id': lesson.topic.id,
                            'topic_name': lesson.topic.name,
                            'lesson_id': lesson.id,
                            'lesson_name': lesson.name
                        })

                # Tìm các bài kiểm tra trong chủ đề
                quizzes = Quiz.objects.filter(lesson__topic__subject_id=subject_id).order_by('?')[:3]

                if quizzes.exists():
                    # Đề xuất bài kiểm tra
                    for quiz in quizzes:
                        recommendations.append({
                            'recommendation_type': 'quiz',
                            'title': f"Làm bài kiểm tra {quiz.title}",
                            'description': f"Bạn cần cải thiện hiệu suất trong chủ đề {subject_name}. Hãy làm bài kiểm tra {quiz.title} để kiểm tra kiến thức của bạn.",
                            'priority': 'medium',
                            'subject_id': subject_id,
                            'subject_name': subject_name,
                            'topic_id': quiz.lesson.topic.id,
                            'topic_name': quiz.lesson.topic.name,
                            'lesson_id': quiz.lesson.id,
                            'lesson_name': quiz.lesson.name,
                            'quiz_id': quiz.id
                        })

                # Tìm các bộ flashcard trong chủ đề
                flashcard_sets = FlashcardSet.objects.filter(lesson__topic__subject_id=subject_id).order_by('?')[:3]

                if flashcard_sets.exists():
                    # Đề xuất bộ flashcard
                    for flashcard_set in flashcard_sets:
                        recommendations.append({
                            'recommendation_type': 'flashcard',
                            'title': f"Ôn tập bộ thẻ {flashcard_set.name}",
                            'description': f"Bạn cần cải thiện hiệu suất trong chủ đề {subject_name}. Hãy ôn tập bộ thẻ {flashcard_set.name} để cải thiện khả năng ghi nhớ của bạn.",
                            'priority': 'medium',
                            'subject_id': subject_id,
                            'subject_name': subject_name,
                            'topic_id': flashcard_set.lesson.topic.id,
                            'topic_name': flashcard_set.lesson.topic.name,
                            'lesson_id': flashcard_set.lesson.id,
                            'lesson_name': flashcard_set.lesson.name,
                            'flashcard_set_id': flashcard_set.id
                        })

        # Đề xuất chủ đề ít được học
        if combined_data:
            # Lấy các chủ đề ít được học nhất
            least_studied_subjects = sorted(combined_data, key=lambda x: x['study_time'])[:3]

            for subject in least_studied_subjects:
                subject_id = subject['subject_id']
                subject_name = subject['subject_name']

                # Tìm các bài học trong chủ đề
                lessons = Lesson.objects.filter(topic__subject_id=subject_id).order_by('topic__order', 'order')[:3]

                if lessons.exists():
                    # Đề xuất bài học
                    for lesson in lessons:
                        recommendations.append({
                            'recommendation_type': 'lesson',
                            'title': f"Khám phá chủ đề {subject_name}",
                            'description': f"Bạn ít học chủ đề {subject_name}. Hãy học bài {lesson.name} để mở rộng kiến thức của bạn.",
                            'priority': 'low',
                            'subject_id': subject_id,
                            'subject_name': subject_name,
                            'topic_id': lesson.topic.id,
                            'topic_name': lesson.topic.name,
                            'lesson_id': lesson.id,
                            'lesson_name': lesson.name
                        })

        # Đề xuất thói quen học tập
        if consistency_score < 50:
            recommendations.append({
                'recommendation_type': 'study_habit',
                'title': "Học tập đều đặn hơn",
                'description': f"Tính đều đặn trong học tập của bạn chỉ đạt {consistency_score}%. Hãy cố gắng học tập ít nhất 30 phút mỗi ngày để cải thiện hiệu quả học tập.",
                'priority': 'high',
                'subject_id': None,
                'subject_name': None,
                'topic_id': None,
                'topic_name': None,
                'lesson_id': None,
                'lesson_name': None
            })

        if focus_score < 50:
            recommendations.append({
                'recommendation_type': 'study_habit',
                'title': "Sử dụng kỹ thuật Pomodoro",
                'description': f"Điểm tập trung của bạn chỉ đạt {focus_score}%. Hãy thử kỹ thuật Pomodoro: học tập tập trung trong 25 phút, sau đó nghỉ ngơi 5 phút. Lặp lại 4 lần, sau đó nghỉ dài 15-30 phút.",
                'priority': 'high',
                'subject_id': None,
                'subject_name': None,
                'topic_id': None,
                'topic_name': None,
                'lesson_id': None,
                'lesson_name': None
            })

        # Sắp xếp các đề xuất theo độ ưu tiên
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))

        return recommendations

    except Exception as e:
        logger.error(f"Lỗi khi lấy đề xuất học tập: {e}")
        return []

def get_strengths(user, days=30):
    """
    Phát hiện điểm mạnh trong học tập của người dùng.

    Args:
        user: Đối tượng User
        days: Số ngày cần lấy dữ liệu (mặc định: 30 ngày)

    Returns:
        list: Danh sách điểm mạnh
    """
    try:
        strengths = []

        # Lấy dữ liệu phân bố thời gian theo chủ đề
        subject_distribution = get_subject_distribution_data(user, days)
        combined_data = subject_distribution.get('combined_data', [])

        # Lấy dữ liệu hiệu suất bài kiểm tra
        quiz_performance = get_quiz_performance_data(user, days)
        quiz_scores_by_subject = quiz_performance.get('quiz_scores_by_subject', [])

        # Lấy dữ liệu hiệu suất flashcard
        flashcard_performance = get_flashcard_performance_data(user, days)
        retention_by_subject = flashcard_performance.get('retention_by_subject', [])

        # Lấy dữ liệu mẫu học tập
        learning_patterns = get_learning_patterns_data(user, days)
        consistency_score = learning_patterns.get('consistency_score', 0)
        focus_score = learning_patterns.get('focus_score', 0)

        # Phát hiện điểm mạnh về chủ đề
        if combined_data:
            # Lấy 3 chủ đề có điểm tổng hợp cao nhất
            top_subjects = combined_data[:3]

            for subject in top_subjects:
                if subject['composite_score'] >= 70:  # Ngưỡng điểm tốt
                    strengths.append({
                        'insight_type': 'strength',
                        'title': f"Bạn học tốt chủ đề {subject['subject_name']}",
                        'description': f"Bạn có hiệu suất tốt trong chủ đề {subject['subject_name']} với điểm tổng hợp {subject['composite_score']}%. Tiếp tục phát huy!",
                        'data_points': subject,
                        'subject_id': subject['subject_id'],
                        'subject_name': subject['subject_name'],
                        'is_highlighted': subject['composite_score'] >= 85
                    })

        # Phát hiện điểm mạnh về bài kiểm tra
        if quiz_scores_by_subject:
            # Lấy 3 chủ đề có điểm bài kiểm tra cao nhất
            top_quiz_subjects = sorted(quiz_scores_by_subject, key=lambda x: x['score'], reverse=True)[:3]

            for subject in top_quiz_subjects:
                if subject['score'] >= 80 and subject['total_quizzes'] >= 3:  # Ngưỡng điểm tốt và ít nhất 3 bài kiểm tra
                    strengths.append({
                        'insight_type': 'strength',
                        'title': f"Bạn làm bài kiểm tra tốt trong chủ đề {subject['subject_name']}",
                        'description': f"Bạn đạt điểm trung bình {subject['score']}% trong {subject['total_quizzes']} bài kiểm tra của chủ đề {subject['subject_name']}. Đây là một kết quả đáng khích lệ!",
                        'data_points': subject,
                        'subject_id': subject['subject_id'],
                        'subject_name': subject['subject_name'],
                        'is_highlighted': subject['score'] >= 90
                    })

        # Phát hiện điểm mạnh về flashcard
        if retention_by_subject:
            # Lấy 3 chủ đề có tỷ lệ ghi nhớ cao nhất
            top_flashcard_subjects = sorted(retention_by_subject, key=lambda x: x['retention_rate'], reverse=True)[:3]

            for subject in top_flashcard_subjects:
                if subject['retention_rate'] >= 75 and subject['total_cards'] >= 10:  # Ngưỡng tỷ lệ ghi nhớ tốt và ít nhất 10 thẻ
                    strengths.append({
                        'insight_type': 'strength',
                        'title': f"Bạn ghi nhớ tốt các thẻ trong chủ đề {subject['subject_name']}",
                        'description': f"Bạn có tỷ lệ ghi nhớ {subject['retention_rate']}% với {subject['total_cards']} thẻ trong chủ đề {subject['subject_name']}. Tiếp tục ôn tập để duy trì kiến thức!",
                        'data_points': subject,
                        'subject_id': subject['subject_id'],
                        'subject_name': subject['subject_name'],
                        'is_highlighted': subject['retention_rate'] >= 85
                    })

        # Phát hiện điểm mạnh về tính đều đặn
        if consistency_score >= 70:  # Ngưỡng tính đều đặn tốt
            strengths.append({
                'insight_type': 'strength',
                'title': "Bạn có tính đều đặn cao trong học tập",
                'description': f"Bạn có tính đều đặn {consistency_score}% trong học tập. Việc học tập đều đặn giúp tăng hiệu quả học tập và ghi nhớ lâu hơn.",
                'data_points': {'consistency_score': consistency_score},
                'subject_id': None,
                'subject_name': None,
                'is_highlighted': consistency_score >= 85
            })

        # Phát hiện điểm mạnh về khả năng tập trung
        if focus_score >= 70:  # Ngưỡng khả năng tập trung tốt
            strengths.append({
                'insight_type': 'strength',
                'title': "Bạn có khả năng tập trung tốt khi học tập",
                'description': f"Bạn có điểm tập trung {focus_score}% khi học tập. Khả năng tập trung tốt giúp bạn tiếp thu kiến thức hiệu quả hơn.",
                'data_points': {'focus_score': focus_score},
                'subject_id': None,
                'subject_name': None,
                'is_highlighted': focus_score >= 85
            })

        return strengths

    except Exception as e:
        logger.error(f"Lỗi khi phát hiện điểm mạnh: {e}")
        return []

def get_learning_insights(user, days=30):
    """
    Lấy phân tích sâu về học tập.

    Args:
        user: Đối tượng User
        days: Số ngày cần lấy dữ liệu (mặc định: 30 ngày)

    Returns:
        list: Danh sách phân tích sâu
    """
    try:
        # Lấy các điểm mạnh
        strengths = get_strengths(user, days)

        # Lấy các điểm yếu
        weaknesses = get_weaknesses(user, days)

        # Lấy các mẫu học tập
        patterns = get_learning_patterns(user, days)

        # Lấy các cải thiện
        improvements = get_improvements(user, days)

        # Lấy các cột mốc
        milestones = get_milestones(user, days)

        # Tổng hợp các phân tích sâu
        insights = strengths + weaknesses + patterns + improvements + milestones

        # Sắp xếp theo mức độ nổi bật và loại phân tích
        insights.sort(key=lambda x: (not x.get('is_highlighted', False), x.get('insight_type')), reverse=False)

        return insights

    except Exception as e:
        logger.error(f"Lỗi khi lấy phân tích sâu về học tập: {e}")
        return []

def generate_report(user, report_type, start_date, end_date, report_format='html', title=None, description=None):
    """
    Tạo báo cáo phân tích.

    Args:
        user: Đối tượng User
        report_type: Loại báo cáo ('daily', 'weekly', 'monthly', 'custom')
        start_date: Ngày bắt đầu
        end_date: Ngày kết thúc
        report_format: Định dạng báo cáo ('html', 'pdf', 'csv', 'json')
        title: Tiêu đề báo cáo
        description: Mô tả báo cáo

    Returns:
        AnalyticsReport: Báo cáo phân tích
    """
    try:
        # Tạo tiêu đề mặc định nếu không có
        if not title:
            if report_type == 'daily':
                title = f"Báo cáo hàng ngày - {start_date.strftime('%d/%m/%Y')}"
            elif report_type == 'weekly':
                title = f"Báo cáo hàng tuần - {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"
            elif report_type == 'monthly':
                title = f"Báo cáo hàng tháng - {start_date.strftime('%m/%Y')}"
            else:  # custom
                title = f"Báo cáo tùy chỉnh - {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"

        # Tạo mô tả mặc định nếu không có
        if not description:
            description = f"Báo cáo phân tích dữ liệu học tập từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"

        # Tính số ngày giữa start_date và end_date
        days = (end_date - start_date).days + 1

        # Lấy dữ liệu cho báo cáo
        report_data = {
            'study_time': get_study_time_data(user, days),
            'quiz_performance': get_quiz_performance_data(user, days),
            'flashcard_performance': get_flashcard_performance_data(user, days),
            'subject_distribution': get_subject_distribution_data(user, days),
            'learning_patterns': get_learning_patterns_data(user, days),
            'insights': get_learning_insights(user, days),
            'recommendations': get_recommendations(user, days)
        }

        # Tạo báo cáo trong cơ sở dữ liệu
        report = AnalyticsReport.objects.create(
            user=user,
            report_type=report_type,
            report_format=report_format,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            report_data=report_data,
            is_generated=True
        )

        # Xử lý tạo file báo cáo nếu cần
        if report_format == 'pdf':
            # Tạo file PDF
            if PDF_SUPPORT:
                file_path = f"reports/{user.username}_{report.id}.pdf"
                # Đảm bảo thư mục reports tồn tại
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                # Tạo file PDF
                pdf_file = generate_pdf_report(report)

                # Lưu file PDF
                with open(file_path, 'wb') as f:
                    f.write(pdf_file.getvalue())

                report.file_path = file_path
                report.save()
            else:
                logger.warning("Không thể tạo báo cáo PDF vì xhtml2pdf không được cài đặt.")
        elif report_format == 'csv':
            # Tạo file CSV
            file_path = f"reports/{user.username}_{report.id}.csv"
            # Đảm bảo thư mục reports tồn tại
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Tạo file CSV
            csv_file = generate_csv_report(report)

            # Lưu file CSV
            if csv_file:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    f.write(csv_file.getvalue())

                report.file_path = file_path
                report.save()
            else:
                logger.warning("Không thể tạo báo cáo CSV.")

        return report

    except Exception as e:
        logger.error(f"Lỗi khi tạo báo cáo phân tích: {e}")
        return None
