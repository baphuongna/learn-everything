import os
import pytesseract
from PIL import Image
from django.conf import settings

# Thử import easyocr, nếu không có thì bỏ qua
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False


class OCRService:
    """
    Dịch vụ nhận dạng ký tự quang học (OCR) sử dụng pytesseract và easyocr
    """

    def __init__(self):
        # Kiểm tra và thiết lập đường dẫn đến Tesseract OCR nếu cần
        if hasattr(settings, 'TESSERACT_CMD_PATH'):
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD_PATH

        # EasyOCR readers sẽ được khởi tạo khi cần
        self.readers = {}

    def recognize_text_tesseract(self, image_path, language='vie'):
        """
        Nhận dạng văn bản từ hình ảnh sử dụng Tesseract OCR

        Args:
            image_path: Đường dẫn đến file hình ảnh
            language: Ngôn ngữ (mặc định: Tiếng Việt)

        Returns:
            str: Văn bản được nhận dạng
        """
        try:
            # Mở và tiền xử lý hình ảnh
            image = Image.open(image_path)

            # Nhận dạng văn bản
            text = pytesseract.image_to_string(image, lang=language)

            return text
        except Exception as e:
            return f"Lỗi khi nhận dạng văn bản: {str(e)}"

    def recognize_text_easyocr(self, image_path, language='vi'):
        """
        Nhận dạng văn bản từ hình ảnh sử dụng EasyOCR

        Args:
            image_path: Đường dẫn đến file hình ảnh
            language: Ngôn ngữ (mặc định: Tiếng Việt)

        Returns:
            str: Văn bản được nhận dạng
        """
        if not EASYOCR_AVAILABLE:
            return "EasyOCR không khả dụng. Vui lòng cài đặt thư viện easyocr."

        try:
            # Khởi tạo reader nếu chưa có
            lang_key = language
            if language == 'vie':
                lang_key = 'vi'
            elif language == 'eng':
                lang_key = 'en'

            if lang_key not in self.readers:
                self.readers[lang_key] = easyocr.Reader([lang_key], gpu=False)

            # Nhận dạng văn bản
            result = self.readers[lang_key].readtext(image_path)

            # Trích xuất văn bản từ kết quả
            text = '\n'.join([item[1] for item in result])

            return text
        except Exception as e:
            return f"Lỗi khi nhận dạng văn bản: {str(e)}"

    def recognize_text(self, image_path, language='vie', use_easyocr=False):
        """
        Nhận dạng văn bản từ hình ảnh

        Args:
            image_path: Đường dẫn đến file hình ảnh
            language: Ngôn ngữ (mặc định: Tiếng Việt)
            use_easyocr: Sử dụng EasyOCR thay vì Tesseract

        Returns:
            str: Văn bản được nhận dạng
        """
        if use_easyocr and EASYOCR_AVAILABLE:
            lang_key = language
            if language == 'vie':
                lang_key = 'vi'
            elif language == 'eng':
                lang_key = 'en'
            return self.recognize_text_easyocr(image_path, lang_key)
        else:
            if use_easyocr and not EASYOCR_AVAILABLE:
                print("EasyOCR không khả dụng, sử dụng Tesseract thay thế")
            return self.recognize_text_tesseract(image_path, language)
