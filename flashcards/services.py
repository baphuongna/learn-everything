"""
Dịch vụ tự động tạo flashcard từ nội dung bài học.
"""
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

# Đảm bảo các tài nguyên NLTK được tải xuống
def ensure_nltk_resources():
    """Đảm bảo các tài nguyên NLTK cần thiết đã được tải xuống."""
    try:
        resources = [
            ('tokenizers/punkt', 'punkt'),
            ('corpora/stopwords', 'stopwords'),
            ('corpora/wordnet', 'wordnet')
        ]
        
        for resource_path, resource_name in resources:
            try:
                nltk.data.find(resource_path)
            except LookupError:
                nltk.download(resource_name, quiet=True)
                
        return True
    except Exception as e:
        logger.error(f"Lỗi khi tải tài nguyên NLTK: {e}")
        return False

# Trích xuất từ khóa từ văn bản
def extract_keywords(text, num_keywords=10, min_word_length=3):
    """
    Trích xuất từ khóa từ văn bản.
    
    Args:
        text (str): Văn bản cần trích xuất từ khóa
        num_keywords (int): Số lượng từ khóa cần trích xuất
        min_word_length (int): Độ dài tối thiểu của từ khóa
        
    Returns:
        list: Danh sách các từ khóa
    """
    try:
        # Đảm bảo tài nguyên NLTK đã được tải xuống
        ensure_nltk_resources()
        
        # Chuyển văn bản thành chữ thường
        text = text.lower()
        
        # Loại bỏ các ký tự đặc biệt
        text = re.sub(r'[^\w\s]', '', text)
        
        # Tokenize văn bản
        words = word_tokenize(text)
        
        # Lấy danh sách stopwords
        stop_words = set(stopwords.words('english'))
        
        # Thêm stopwords tiếng Việt
        vietnamese_stop_words = {
            'và', 'là', 'của', 'có', 'được', 'trong', 'đã', 'cho', 'không', 'với',
            'các', 'này', 'những', 'một', 'về', 'để', 'từ', 'khi', 'đến', 'như',
            'cũng', 'theo', 'tại', 'vì', 'nên', 'sẽ', 'rằng', 'tuy', 'nhưng', 'mà',
            'thì', 'nếu', 'bởi', 'vậy', 'do', 'còn', 'nữa', 'đang', 'rất', 'quá'
        }
        stop_words.update(vietnamese_stop_words)
        
        # Loại bỏ stopwords và từ ngắn
        filtered_words = [word for word in words if word not in stop_words and len(word) >= min_word_length]
        
        # Đếm tần suất xuất hiện của từng từ
        word_counts = Counter(filtered_words)
        
        # Lấy các từ khóa phổ biến nhất
        keywords = [word for word, count in word_counts.most_common(num_keywords)]
        
        return keywords
    except Exception as e:
        logger.error(f"Lỗi khi trích xuất từ khóa: {e}")
        return []

# Trích xuất định nghĩa cho từ khóa
def extract_definitions(text, keywords):
    """
    Trích xuất định nghĩa cho từ khóa từ văn bản.
    
    Args:
        text (str): Văn bản cần trích xuất định nghĩa
        keywords (list): Danh sách các từ khóa
        
    Returns:
        dict: Từ điển với khóa là từ khóa và giá trị là định nghĩa
    """
    try:
        # Đảm bảo tài nguyên NLTK đã được tải xuống
        ensure_nltk_resources()
        
        # Tách văn bản thành các câu
        sentences = sent_tokenize(text)
        
        # Tạo từ điển để lưu trữ từ khóa và định nghĩa
        definitions = {}
        
        # Tìm câu chứa từ khóa
        for keyword in keywords:
            for sentence in sentences:
                # Kiểm tra xem từ khóa có trong câu không (không phân biệt chữ hoa/thường)
                if re.search(r'\b' + re.escape(keyword) + r'\b', sentence, re.IGNORECASE):
                    # Nếu từ khóa đã có trong từ điển, thêm câu vào định nghĩa
                    if keyword in definitions:
                        definitions[keyword] += " " + sentence.strip()
                    else:
                        definitions[keyword] = sentence.strip()
                    break
        
        # Nếu không tìm thấy định nghĩa cho từ khóa, tìm câu chứa từ khóa
        for keyword in keywords:
            if keyword not in definitions:
                for sentence in sentences:
                    if keyword.lower() in sentence.lower():
                        definitions[keyword] = sentence.strip()
                        break
        
        return definitions
    except Exception as e:
        logger.error(f"Lỗi khi trích xuất định nghĩa: {e}")
        return {}

# Trích xuất cặp từ khóa-định nghĩa từ văn bản có cấu trúc
def extract_structured_pairs(text):
    """
    Trích xuất cặp từ khóa-định nghĩa từ văn bản có cấu trúc.
    
    Args:
        text (str): Văn bản cần trích xuất
        
    Returns:
        list: Danh sách các cặp (từ khóa, định nghĩa)
    """
    try:
        pairs = []
        
        # Tìm các cặp từ khóa-định nghĩa theo định dạng "Từ khóa: Định nghĩa"
        pattern1 = r'([^:]+):\s*(.+)'
        matches1 = re.findall(pattern1, text)
        for keyword, definition in matches1:
            keyword = keyword.strip()
            definition = definition.strip()
            if keyword and definition:
                pairs.append((keyword, definition))
        
        # Tìm các cặp từ khóa-định nghĩa theo định dạng "Từ khóa - Định nghĩa"
        pattern2 = r'([^-]+)\s*-\s*(.+)'
        matches2 = re.findall(pattern2, text)
        for keyword, definition in matches2:
            keyword = keyword.strip()
            definition = definition.strip()
            if keyword and definition and (keyword, definition) not in pairs:
                pairs.append((keyword, definition))
        
        # Tìm các cặp từ khóa-định nghĩa theo định dạng "• Từ khóa: Định nghĩa"
        pattern3 = r'[•\*]\s*([^:]+):\s*(.+)'
        matches3 = re.findall(pattern3, text)
        for keyword, definition in matches3:
            keyword = keyword.strip()
            definition = definition.strip()
            if keyword and definition and (keyword, definition) not in pairs:
                pairs.append((keyword, definition))
        
        return pairs
    except Exception as e:
        logger.error(f"Lỗi khi trích xuất cặp từ khóa-định nghĩa: {e}")
        return []

# Tạo flashcards từ nội dung bài học
def generate_flashcards_from_lesson(lesson, max_cards=10):
    """
    Tạo flashcards từ nội dung bài học.
    
    Args:
        lesson: Đối tượng Lesson
        max_cards (int): Số lượng flashcard tối đa cần tạo
        
    Returns:
        list: Danh sách các cặp (front, back) cho flashcard
    """
    try:
        flashcards = []
        
        # Trích xuất cặp từ khóa-định nghĩa từ văn bản có cấu trúc
        structured_pairs = extract_structured_pairs(lesson.content)
        
        # Nếu tìm thấy các cặp có cấu trúc, sử dụng chúng
        if structured_pairs:
            flashcards.extend(structured_pairs[:max_cards])
        
        # Nếu chưa đủ số lượng flashcard, trích xuất từ khóa và định nghĩa
        if len(flashcards) < max_cards:
            remaining = max_cards - len(flashcards)
            
            # Trích xuất từ khóa
            keywords = extract_keywords(lesson.content, num_keywords=remaining)
            
            # Trích xuất định nghĩa cho từ khóa
            definitions = extract_definitions(lesson.content, keywords)
            
            # Thêm vào danh sách flashcard
            for keyword in keywords:
                if keyword in definitions:
                    flashcards.append((keyword, definitions[keyword]))
        
        return flashcards
    except Exception as e:
        logger.error(f"Lỗi khi tạo flashcards từ bài học: {e}")
        return []
