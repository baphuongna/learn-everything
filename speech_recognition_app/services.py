import os
import tempfile
import speech_recognition as sr
from django.conf import settings

# Thử import whisper, nếu không có thì bỏ qua
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class SpeechRecognitionService:
    """
    Dịch vụ nhận diện giọng nói sử dụng SpeechRecognition và Whisper
    """

    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Khởi tạo model Whisper (sẽ tải về nếu chưa có)
        self.whisper_model = None  # Sẽ được tải khi cần thiết

    def recognize_from_file(self, audio_file_path, language='vi-VN', use_whisper=False):
        """
        Nhận diện giọng nói từ file âm thanh

        Args:
            audio_file_path: Đường dẫn đến file âm thanh
            language: Ngôn ngữ (mặc định: Tiếng Việt)
            use_whisper: Sử dụng Whisper thay vì Google Speech Recognition

        Returns:
            str: Văn bản được nhận diện
        """
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio_data = self.recognizer.record(source)

                if use_whisper and WHISPER_AVAILABLE:
                    # Sử dụng Whisper
                    if self.whisper_model is None:
                        self.whisper_model = whisper.load_model("base")

                    # Lưu audio_data tạm thời để Whisper xử lý
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                        temp_path = temp_file.name

                    with open(temp_path, "wb") as f:
                        f.write(audio_data.get_wav_data())

                    result = self.whisper_model.transcribe(temp_path)
                    os.remove(temp_path)  # Xóa file tạm
                    return result["text"]
                else:
                    # Sử dụng Google Speech Recognition hoặc nếu Whisper không khả dụng
                    if use_whisper and not WHISPER_AVAILABLE:
                        print("Whisper không khả dụng, sử dụng Google Speech Recognition thay thế")
                    return self.recognizer.recognize_google(audio_data, language=language)
        except sr.UnknownValueError:
            return "Không thể nhận diện giọng nói"
        except sr.RequestError as e:
            return f"Lỗi kết nối đến dịch vụ nhận diện giọng nói: {e}"
        except Exception as e:
            return f"Lỗi: {str(e)}"

    def recognize_from_microphone(self, duration=5, language='vi-VN', use_whisper=False):
        """
        Nhận diện giọng nói từ microphone

        Args:
            duration: Thời gian ghi âm (giây)
            language: Ngôn ngữ (mặc định: Tiếng Việt)
            use_whisper: Sử dụng Whisper thay vì Google Speech Recognition

        Returns:
            str: Văn bản được nhận diện
        """
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                print("Đang lắng nghe...")
                audio_data = self.recognizer.listen(source, timeout=duration)

                if use_whisper and WHISPER_AVAILABLE:
                    # Sử dụng Whisper
                    if self.whisper_model is None:
                        self.whisper_model = whisper.load_model("base")

                    # Lưu audio_data tạm thời để Whisper xử lý
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                        temp_path = temp_file.name

                    with open(temp_path, "wb") as f:
                        f.write(audio_data.get_wav_data())

                    result = self.whisper_model.transcribe(temp_path)
                    os.remove(temp_path)  # Xóa file tạm
                    return result["text"]
                else:
                    # Sử dụng Google Speech Recognition hoặc nếu Whisper không khả dụng
                    if use_whisper and not WHISPER_AVAILABLE:
                        print("Whisper không khả dụng, sử dụng Google Speech Recognition thay thế")
                    return self.recognizer.recognize_google(audio_data, language=language)
        except sr.UnknownValueError:
            return "Không thể nhận diện giọng nói"
        except sr.RequestError as e:
            return f"Lỗi kết nối đến dịch vụ nhận diện giọng nói: {e}"
        except Exception as e:
            return f"Lỗi: {str(e)}"
