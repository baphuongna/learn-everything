import os
import tempfile
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import SpeechRecognitionResult
from .services import SpeechRecognitionService
from .pronunciation_service import PronunciationEvaluationService
from .forms import AudioUploadForm, PronunciationEvaluationForm


@login_required
def speech_recognition_home(request):
    """Trang chủ nhận diện giọng nói"""
    recent_results = SpeechRecognitionResult.objects.filter(user=request.user).order_by('-created_at')[:5]
    form = AudioUploadForm()

    context = {
        'recent_results': recent_results,
        'form': form,
    }

    return render(request, 'speech_recognition_app/home.html', context)


@login_required
@require_POST
def upload_audio(request):
    """Xử lý upload file âm thanh"""
    form = AudioUploadForm(request.POST, request.FILES)

    if form.is_valid():
        audio_file = request.FILES['audio_file']
        language = form.cleaned_data['language']
        use_whisper = form.cleaned_data['use_whisper']

        # Lưu file tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            # Nhận diện giọng nói
            service = SpeechRecognitionService()
            text_result = service.recognize_from_file(
                temp_file_path,
                language=language,
                use_whisper=use_whisper
            )

            # Lưu kết quả vào database
            result = SpeechRecognitionResult.objects.create(
                user=request.user,
                audio_file=audio_file,
                text_result=text_result
            )

            messages.success(request, 'Nhận diện giọng nói thành công!')

            # Xóa file tạm
            os.unlink(temp_file_path)

            return redirect('speech_recognition_result', result_id=result.id)

        except Exception as e:
            # Xóa file tạm nếu có lỗi
            os.unlink(temp_file_path)
            messages.error(request, f'Lỗi khi nhận diện giọng nói: {str(e)}')
            return redirect('speech_recognition_home')

    messages.error(request, 'Form không hợp lệ. Vui lòng thử lại.')
    return redirect('speech_recognition_home')


@login_required
def record_audio(request):
    """Trang ghi âm trực tiếp"""
    return render(request, 'speech_recognition_app/record.html')


@login_required
@require_POST
def process_recorded_audio(request):
    """Xử lý âm thanh được ghi trực tiếp"""
    if 'audio_data' not in request.FILES:
        return JsonResponse({'error': 'Không tìm thấy dữ liệu âm thanh'}, status=400)

    audio_file = request.FILES['audio_data']
    language = request.POST.get('language', 'vi-VN')
    use_whisper = request.POST.get('use_whisper', 'false').lower() == 'true'

    # Lưu file tạm thời
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        for chunk in audio_file.chunks():
            temp_file.write(chunk)
        temp_file_path = temp_file.name

    try:
        # Nhận diện giọng nói
        service = SpeechRecognitionService()
        text_result = service.recognize_from_file(
            temp_file_path,
            language=language,
            use_whisper=use_whisper
        )

        # Lưu kết quả vào database
        result = SpeechRecognitionResult.objects.create(
            user=request.user,
            audio_file=audio_file,
            text_result=text_result
        )

        # Xóa file tạm
        os.unlink(temp_file_path)

        return JsonResponse({
            'success': True,
            'text': text_result,
            'result_id': result.id
        })

    except Exception as e:
        # Xóa file tạm nếu có lỗi
        os.unlink(temp_file_path)
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def speech_recognition_result(request, result_id):
    """Hiển thị kết quả nhận diện giọng nói"""
    try:
        result = SpeechRecognitionResult.objects.get(id=result_id, user=request.user)
        return render(request, 'speech_recognition_app/result.html', {'result': result})
    except SpeechRecognitionResult.DoesNotExist:
        messages.error(request, 'Không tìm thấy kết quả nhận diện giọng nói')
        return redirect('speech_recognition_home')


@login_required
def speech_recognition_history(request):
    """Lịch sử nhận diện giọng nói"""
    results = SpeechRecognitionResult.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'speech_recognition_app/history.html', {'results': results})


@login_required
def pronunciation_evaluation(request):
    """Trang đánh giá phát âm"""
    form = PronunciationEvaluationForm()
    recent_results = SpeechRecognitionResult.objects.filter(
        user=request.user,
        pronunciation_score__isnull=False
    ).order_by('-created_at')[:5]

    context = {
        'form': form,
        'recent_results': recent_results,
    }

    return render(request, 'speech_recognition_app/pronunciation_evaluation.html', context)


@login_required
@require_POST
def evaluate_pronunciation(request):
    """Xử lý đánh giá phát âm"""
    form = PronunciationEvaluationForm(request.POST, request.FILES)

    if form.is_valid():
        audio_file = request.FILES['audio_file']
        expected_text = form.cleaned_data['expected_text']
        language = form.cleaned_data['language']
        use_whisper = form.cleaned_data['use_whisper']

        # Lưu file tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            # Nhận diện giọng nói
            speech_service = SpeechRecognitionService()
            text_result = speech_service.recognize_from_file(
                temp_file_path,
                language=language,
                use_whisper=use_whisper
            )

            # Đánh giá phát âm
            pronunciation_service = PronunciationEvaluationService()
            evaluation_result = pronunciation_service.evaluate_pronunciation(
                text_result,
                expected_text,
                language
            )

            # Lưu kết quả vào database
            result = SpeechRecognitionResult.objects.create(
                user=request.user,
                audio_file=audio_file,
                text_result=text_result,
                expected_text=expected_text,
                language=language,
                pronunciation_score=evaluation_result['pronunciation_score'],
                accuracy_score=evaluation_result['accuracy_score'],
                fluency_score=evaluation_result['fluency_score'],
                feedback=evaluation_result['feedback']
            )

            messages.success(request, 'Đánh giá phát âm thành công!')

            # Xóa file tạm
            os.unlink(temp_file_path)

            return redirect('pronunciation_evaluation_result', result_id=result.id)

        except Exception as e:
            # Xóa file tạm nếu có lỗi
            os.unlink(temp_file_path)
            messages.error(request, f'Lỗi khi đánh giá phát âm: {str(e)}')
            return redirect('pronunciation_evaluation')

    messages.error(request, 'Form không hợp lệ. Vui lòng thử lại.')
    return redirect('pronunciation_evaluation')


@login_required
def pronunciation_evaluation_result(request, result_id):
    """Hiển thị kết quả đánh giá phát âm"""
    try:
        result = SpeechRecognitionResult.objects.get(id=result_id, user=request.user)

        if not result.pronunciation_score:
            messages.warning(request, 'Kết quả này không có đánh giá phát âm.')
            return redirect('speech_recognition_result', result_id=result.id)

        return render(request, 'speech_recognition_app/pronunciation_result.html', {'result': result})
    except SpeechRecognitionResult.DoesNotExist:
        messages.error(request, 'Không tìm thấy kết quả đánh giá phát âm')
        return redirect('pronunciation_evaluation')


@login_required
def pronunciation_history(request):
    """Lịch sử đánh giá phát âm"""
    results = SpeechRecognitionResult.objects.filter(
        user=request.user,
        pronunciation_score__isnull=False
    ).order_by('-created_at')

    return render(request, 'speech_recognition_app/pronunciation_history.html', {'results': results})
