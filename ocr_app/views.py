import os
import tempfile
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import OCRResult
from .services import OCRService
from .forms import ImageUploadForm


@login_required
def ocr_home(request):
    """Trang chủ OCR"""
    recent_results = OCRResult.objects.filter(user=request.user).order_by('-created_at')[:5]
    form = ImageUploadForm()
    
    context = {
        'recent_results': recent_results,
        'form': form,
    }
    
    return render(request, 'ocr_app/home.html', context)


@login_required
@require_POST
def upload_image(request):
    """Xử lý upload hình ảnh"""
    form = ImageUploadForm(request.POST, request.FILES)
    
    if form.is_valid():
        image_file = request.FILES['image']
        language = form.cleaned_data['language']
        use_easyocr = form.cleaned_data['use_easyocr']
        
        # Lưu file tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_file.name)[1]) as temp_file:
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Nhận dạng văn bản
            service = OCRService()
            text_result = service.recognize_text(
                temp_file_path, 
                language=language,
                use_easyocr=use_easyocr
            )
            
            # Lưu kết quả vào database
            result = OCRResult.objects.create(
                user=request.user,
                image=image_file,
                text_result=text_result,
                language=language
            )
            
            messages.success(request, 'Nhận dạng văn bản thành công!')
            
            # Xóa file tạm
            os.unlink(temp_file_path)
            
            return redirect('ocr_result', result_id=result.id)
        
        except Exception as e:
            # Xóa file tạm nếu có lỗi
            os.unlink(temp_file_path)
            messages.error(request, f'Lỗi khi nhận dạng văn bản: {str(e)}')
            return redirect('ocr_home')
    
    messages.error(request, 'Form không hợp lệ. Vui lòng thử lại.')
    return redirect('ocr_home')


@login_required
def ocr_result(request, result_id):
    """Hiển thị kết quả OCR"""
    try:
        result = OCRResult.objects.get(id=result_id, user=request.user)
        return render(request, 'ocr_app/result.html', {'result': result})
    except OCRResult.DoesNotExist:
        messages.error(request, 'Không tìm thấy kết quả OCR')
        return redirect('ocr_home')


@login_required
def ocr_history(request):
    """Lịch sử OCR"""
    results = OCRResult.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'ocr_app/history.html', {'results': results})
