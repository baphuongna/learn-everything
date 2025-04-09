from django import forms


class ImageUploadForm(forms.Form):
    """Form để upload hình ảnh cho OCR"""
    
    image = forms.ImageField(
        label='Hình ảnh',
        help_text='Hỗ trợ các định dạng: JPG, PNG, BMP, TIFF'
    )
    
    language = forms.ChoiceField(
        label='Ngôn ngữ',
        choices=[
            ('vie', 'Tiếng Việt'),
            ('eng', 'Tiếng Anh'),
            ('fra', 'Tiếng Pháp'),
            ('deu', 'Tiếng Đức'),
            ('jpn', 'Tiếng Nhật'),
            ('kor', 'Tiếng Hàn'),
            ('chi_sim', 'Tiếng Trung (Giản thể)'),
            ('chi_tra', 'Tiếng Trung (Phồn thể)'),
        ],
        initial='vie'
    )
    
    use_easyocr = forms.BooleanField(
        label='Sử dụng EasyOCR (chính xác hơn cho một số ngôn ngữ)',
        required=False,
        initial=False
    )
