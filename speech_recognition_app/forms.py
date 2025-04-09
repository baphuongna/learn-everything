from django import forms


class AudioUploadForm(forms.Form):
    audio_file = forms.FileField(
        label='File âm thanh',
        help_text='Hỗ trợ các định dạng: WAV, FLAC, MP3'
    )
    language = forms.ChoiceField(
        label='Ngôn ngữ',
        choices=[
            ('vi-VN', 'Tiếng Việt'),
            ('en-US', 'Tiếng Anh (US)'),
            ('en-GB', 'Tiếng Anh (UK)'),
            ('fr-FR', 'Tiếng Pháp'),
            ('de-DE', 'Tiếng Đức'),
            ('ja-JP', 'Tiếng Nhật'),
            ('ko-KR', 'Tiếng Hàn'),
            ('zh-CN', 'Tiếng Trung (Giản thể)'),
            ('zh-TW', 'Tiếng Trung (Phồn thể)'),
        ],
        initial='vi-VN'
    )
    use_whisper = forms.BooleanField(
        label='Sử dụng Whisper (chính xác hơn nhưng chậm hơn)',
        required=False,
        initial=False
    )


class PronunciationEvaluationForm(forms.Form):
    audio_file = forms.FileField(
        label='File âm thanh',
        help_text='Hỗ trợ các định dạng: WAV, FLAC, MP3'
    )
    expected_text = forms.CharField(
        label='Văn bản mẫu',
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text='Nhập văn bản mẫu để so sánh với kết quả nhận diện'
    )
    language = forms.ChoiceField(
        label='Ngôn ngữ',
        choices=[
            ('vi-VN', 'Tiếng Việt'),
            ('en-US', 'Tiếng Anh (US)'),
            ('en-GB', 'Tiếng Anh (UK)'),
            ('fr-FR', 'Tiếng Pháp'),
            ('de-DE', 'Tiếng Đức'),
            ('ja-JP', 'Tiếng Nhật'),
            ('ko-KR', 'Tiếng Hàn'),
            ('zh-CN', 'Tiếng Trung (Giản thể)'),
            ('zh-TW', 'Tiếng Trung (Phồn thể)'),
        ],
        initial='vi-VN'
    )
    use_whisper = forms.BooleanField(
        label='Sử dụng Whisper (chính xác hơn nhưng chậm hơn)',
        required=False,
        initial=True
    )
