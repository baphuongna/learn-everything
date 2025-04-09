import re
import difflib
import nltk
from nltk.metrics import edit_distance
from django.conf import settings
import requests
import json
import os

# Đảm bảo NLTK đã tải các dữ liệu cần thiết
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


class PronunciationEvaluationService:
    """
    Dịch vụ đánh giá phát âm dựa trên kết quả nhận diện giọng nói
    """
    
    def __init__(self):
        self.openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
    
    def evaluate_pronunciation(self, recognized_text, expected_text, language='vi-VN'):
        """
        Đánh giá phát âm dựa trên văn bản nhận diện và văn bản mẫu
        
        Args:
            recognized_text: Văn bản được nhận diện từ giọng nói
            expected_text: Văn bản mẫu để so sánh
            language: Ngôn ngữ đánh giá
            
        Returns:
            dict: Kết quả đánh giá bao gồm các điểm số và phản hồi
        """
        if not recognized_text or not expected_text:
            return {
                'pronunciation_score': None,
                'accuracy_score': None,
                'fluency_score': None,
                'feedback': "Không thể đánh giá do thiếu văn bản nhận diện hoặc văn bản mẫu."
            }
        
        # Chuẩn hóa văn bản
        recognized_text = self._normalize_text(recognized_text)
        expected_text = self._normalize_text(expected_text)
        
        # Tính điểm chính xác
        accuracy_score = self._calculate_accuracy_score(recognized_text, expected_text)
        
        # Tính điểm phát âm và trôi chảy
        pronunciation_score, fluency_score = self._calculate_pronunciation_fluency_scores(
            recognized_text, expected_text, accuracy_score
        )
        
        # Tạo phản hồi chi tiết
        feedback = self._generate_feedback(
            recognized_text, expected_text, pronunciation_score, accuracy_score, fluency_score, language
        )
        
        return {
            'pronunciation_score': pronunciation_score,
            'accuracy_score': accuracy_score,
            'fluency_score': fluency_score,
            'feedback': feedback
        }
    
    def _normalize_text(self, text):
        """Chuẩn hóa văn bản để so sánh"""
        if not text:
            return ""
        
        # Chuyển về chữ thường
        text = text.lower()
        
        # Loại bỏ dấu câu
        text = re.sub(r'[^\w\s]', '', text)
        
        # Loại bỏ khoảng trắng thừa
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _calculate_accuracy_score(self, recognized_text, expected_text):
        """Tính điểm chính xác dựa trên độ tương đồng giữa hai văn bản"""
        if not recognized_text or not expected_text:
            return 0
        
        # Tách thành các từ
        recognized_words = recognized_text.split()
        expected_words = expected_text.split()
        
        # Tính tỷ lệ từ chính xác
        matcher = difflib.SequenceMatcher(None, recognized_text, expected_text)
        similarity_ratio = matcher.ratio() * 100
        
        # Tính khoảng cách Levenshtein và chuẩn hóa
        max_length = max(len(recognized_text), len(expected_text))
        if max_length == 0:
            return 0
            
        levenshtein_distance = edit_distance(recognized_text, expected_text)
        levenshtein_score = max(0, 100 - (levenshtein_distance / max_length * 100))
        
        # Kết hợp các điểm số
        accuracy_score = (similarity_ratio + levenshtein_score) / 2
        
        return min(100, max(0, accuracy_score))
    
    def _calculate_pronunciation_fluency_scores(self, recognized_text, expected_text, accuracy_score):
        """
        Tính điểm phát âm và trôi chảy dựa trên độ chính xác và các yếu tố khác
        
        Lưu ý: Đánh giá phát âm chính xác cần các công cụ chuyên biệt như Azure Speech Service
        hoặc các mô hình đánh giá phát âm. Ở đây chúng ta sử dụng phương pháp đơn giản hơn.
        """
        # Điểm phát âm dựa trên độ chính xác, nhưng có thể thấp hơn nếu có lỗi phát âm
        pronunciation_score = accuracy_score * 0.9  # Giả định
        
        # Điểm trôi chảy dựa trên độ dài văn bản và tốc độ nói (giả định)
        expected_length = len(expected_text.split())
        recognized_length = len(recognized_text.split())
        
        length_ratio = min(recognized_length / max(1, expected_length), 1.0)
        fluency_score = accuracy_score * 0.7 + length_ratio * 30
        
        return min(100, max(0, pronunciation_score)), min(100, max(0, fluency_score))
    
    def _generate_feedback(self, recognized_text, expected_text, pronunciation_score, 
                          accuracy_score, fluency_score, language):
        """Tạo phản hồi chi tiết về phát âm"""
        # Phản hồi cơ bản
        if accuracy_score >= 90:
            basic_feedback = "Phát âm rất tốt! Bạn đã phát âm chính xác hầu hết các từ."
        elif accuracy_score >= 75:
            basic_feedback = "Phát âm tốt. Có một vài từ cần cải thiện."
        elif accuracy_score >= 50:
            basic_feedback = "Phát âm trung bình. Cần cải thiện nhiều từ."
        else:
            basic_feedback = "Cần cải thiện phát âm nhiều hơn. Hãy luyện tập thêm."
        
        # Phân tích sự khác biệt
        diff_analysis = self._analyze_differences(recognized_text, expected_text)
        
        # Sử dụng AI để tạo phản hồi chi tiết nếu có API key
        ai_feedback = ""
        if self.openai_api_key and accuracy_score < 95:
            ai_feedback = self._get_ai_feedback(recognized_text, expected_text, language)
        
        # Kết hợp phản hồi
        feedback = f"{basic_feedback}\n\n"
        
        if diff_analysis:
            feedback += f"Chi tiết:\n{diff_analysis}\n\n"
        
        if ai_feedback:
            feedback += f"Gợi ý cải thiện:\n{ai_feedback}\n\n"
        
        feedback += f"Điểm phát âm: {pronunciation_score:.1f}/100\n"
        feedback += f"Điểm chính xác: {accuracy_score:.1f}/100\n"
        feedback += f"Điểm trôi chảy: {fluency_score:.1f}/100\n"
        
        return feedback
    
    def _analyze_differences(self, recognized_text, expected_text):
        """Phân tích sự khác biệt giữa văn bản nhận diện và văn bản mẫu"""
        recognized_words = recognized_text.split()
        expected_words = expected_text.split()
        
        # Sử dụng difflib để tìm sự khác biệt
        matcher = difflib.SequenceMatcher(None, recognized_words, expected_words)
        diff_blocks = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                diff_blocks.append(f"- Thay thế: '{' '.join(recognized_words[i1:i2])}' thành '{' '.join(expected_words[j1:j2])}'")
            elif tag == 'delete':
                diff_blocks.append(f"- Xóa: '{' '.join(recognized_words[i1:i2])}'")
            elif tag == 'insert':
                diff_blocks.append(f"- Thêm: '{' '.join(expected_words[j1:j2])}'")
        
        return "\n".join(diff_blocks) if diff_blocks else "Không có sự khác biệt đáng kể."
    
    def _get_ai_feedback(self, recognized_text, expected_text, language):
        """Sử dụng OpenAI API để tạo phản hồi chi tiết về phát âm"""
        if not self.openai_api_key:
            return ""
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            prompt = f"""
            Hãy đánh giá phát âm dựa trên kết quả nhận diện giọng nói sau:
            
            Văn bản mẫu: "{expected_text}"
            Văn bản nhận diện: "{recognized_text}"
            Ngôn ngữ: {language}
            
            Hãy cung cấp:
            1. Phân tích các lỗi phát âm cụ thể
            2. Gợi ý cách cải thiện phát âm
            3. Các bài tập luyện phát âm phù hợp
            
            Trả lời ngắn gọn, súc tích và hữu ích.
            """
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                return ""
        except Exception as e:
            return ""
