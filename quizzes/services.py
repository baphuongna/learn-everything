"""
Dịch vụ tự động tạo câu hỏi kiểm tra từ nội dung bài học.
"""
import re
import nltk
import random
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter
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

# Trích xuất câu quan trọng từ văn bản
def extract_important_sentences(text, num_sentences=10):
    """
    Trích xuất các câu quan trọng từ văn bản.
    
    Args:
        text (str): Văn bản cần trích xuất
        num_sentences (int): Số lượng câu cần trích xuất
        
    Returns:
        list: Danh sách các câu quan trọng
    """
    try:
        # Đảm bảo tài nguyên NLTK đã được tải xuống
        ensure_nltk_resources()
        
        # Tách văn bản thành các câu
        sentences = sent_tokenize(text)
        
        # Nếu số câu ít hơn số lượng cần trích xuất, trả về tất cả
        if len(sentences) <= num_sentences:
            return sentences
        
        # Tính điểm cho mỗi câu dựa trên số từ quan trọng
        sentence_scores = {}
        
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
        
        # Tính điểm cho mỗi câu
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            word_count = len([word for word in words if word not in stop_words])
            sentence_scores[sentence] = word_count
        
        # Sắp xếp câu theo điểm số và lấy các câu có điểm cao nhất
        important_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        return [sentence for sentence, score in important_sentences[:num_sentences]]
    
    except Exception as e:
        logger.error(f"Lỗi khi trích xuất câu quan trọng: {e}")
        return []

# Tạo câu hỏi từ câu
def generate_question_from_sentence(sentence):
    """
    Tạo câu hỏi từ câu.
    
    Args:
        sentence (str): Câu cần tạo câu hỏi
        
    Returns:
        tuple: (câu hỏi, đáp án đúng)
    """
    try:
        # Loại bỏ dấu câu ở cuối
        sentence = re.sub(r'[.!?]$', '', sentence)
        
        # Tách câu thành các từ
        words = word_tokenize(sentence)
        
        # Nếu câu quá ngắn, không tạo câu hỏi
        if len(words) < 5:
            return None, None
        
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
        
        # Tìm các từ quan trọng (không phải stopword)
        important_words = [word for word in words if word.lower() not in stop_words and len(word) > 3]
        
        # Nếu không có từ quan trọng, không tạo câu hỏi
        if not important_words:
            return None, None
        
        # Chọn một từ quan trọng ngẫu nhiên để thay thế
        word_to_replace = random.choice(important_words)
        word_index = words.index(word_to_replace)
        
        # Tạo câu hỏi bằng cách thay thế từ bằng dấu "..."
        question_words = words.copy()
        question_words[word_index] = "..."
        
        # Tạo câu hỏi
        question = " ".join(question_words)
        
        # Thêm dấu hỏi nếu cần
        if not question.endswith('?'):
            question += "?"
        
        return question, word_to_replace
    
    except Exception as e:
        logger.error(f"Lỗi khi tạo câu hỏi từ câu: {e}")
        return None, None

# Tạo câu hỏi trắc nghiệm từ câu
def generate_multiple_choice_question(sentence, all_sentences):
    """
    Tạo câu hỏi trắc nghiệm từ câu.
    
    Args:
        sentence (str): Câu cần tạo câu hỏi
        all_sentences (list): Tất cả các câu trong văn bản
        
    Returns:
        dict: Thông tin câu hỏi trắc nghiệm
    """
    try:
        # Tạo câu hỏi từ câu
        question, correct_answer = generate_question_from_sentence(sentence)
        
        # Nếu không tạo được câu hỏi, trả về None
        if not question or not correct_answer:
            return None
        
        # Tạo các đáp án nhiễu
        distractors = []
        
        # Lấy tất cả các từ từ các câu khác
        all_words = []
        for s in all_sentences:
            if s != sentence:
                words = word_tokenize(s)
                all_words.extend(words)
        
        # Lọc các từ có độ dài tương tự với đáp án đúng
        similar_words = [word for word in all_words if abs(len(word) - len(correct_answer)) <= 2]
        
        # Nếu không có đủ từ tương tự, sử dụng tất cả các từ
        if len(similar_words) < 3:
            similar_words = all_words
        
        # Loại bỏ các từ trùng với đáp án đúng
        similar_words = [word for word in similar_words if word.lower() != correct_answer.lower()]
        
        # Chọn ngẫu nhiên 3 từ làm đáp án nhiễu
        if len(similar_words) >= 3:
            distractors = random.sample(similar_words, 3)
        else:
            # Nếu không có đủ từ, tạo các đáp án nhiễu đơn giản
            distractors = [f"Đáp án {i+1}" for i in range(3)]
        
        # Tạo danh sách tất cả các đáp án
        all_answers = [correct_answer] + distractors
        
        # Xáo trộn các đáp án
        random.shuffle(all_answers)
        
        # Tìm vị trí của đáp án đúng
        correct_index = all_answers.index(correct_answer)
        
        return {
            'question': question,
            'answers': all_answers,
            'correct_index': correct_index
        }
    
    except Exception as e:
        logger.error(f"Lỗi khi tạo câu hỏi trắc nghiệm: {e}")
        return None

# Tạo câu hỏi đúng/sai từ câu
def generate_true_false_question(sentence):
    """
    Tạo câu hỏi đúng/sai từ câu.
    
    Args:
        sentence (str): Câu cần tạo câu hỏi
        
    Returns:
        dict: Thông tin câu hỏi đúng/sai
    """
    try:
        # Loại bỏ dấu câu ở cuối
        sentence = re.sub(r'[.!?]$', '', sentence)
        
        # Quyết định ngẫu nhiên xem câu hỏi là đúng hay sai
        is_true = random.choice([True, False])
        
        if is_true:
            # Nếu câu hỏi là đúng, sử dụng câu gốc
            question = sentence
        else:
            # Nếu câu hỏi là sai, thay đổi một phần của câu
            words = word_tokenize(sentence)
            
            # Nếu câu quá ngắn, không tạo câu hỏi
            if len(words) < 5:
                return None
            
            # Chọn một vị trí ngẫu nhiên để thay đổi
            index_to_change = random.randint(0, len(words) - 1)
            
            # Thay đổi từ tại vị trí đó
            words[index_to_change] = "KHÔNG" if random.random() < 0.5 else "CÓ"
            
            # Tạo câu hỏi mới
            question = " ".join(words)
        
        return {
            'question': question,
            'is_true': is_true
        }
    
    except Exception as e:
        logger.error(f"Lỗi khi tạo câu hỏi đúng/sai: {e}")
        return None

# Tạo câu hỏi kiểm tra từ nội dung bài học
def generate_quiz_from_lesson(lesson, num_questions=10):
    """
    Tạo câu hỏi kiểm tra từ nội dung bài học.
    
    Args:
        lesson: Đối tượng Lesson
        num_questions (int): Số lượng câu hỏi cần tạo
        
    Returns:
        dict: Thông tin bài kiểm tra
    """
    try:
        # Trích xuất các câu quan trọng từ nội dung bài học
        important_sentences = extract_important_sentences(lesson.content, num_questions * 2)
        
        # Tạo câu hỏi trắc nghiệm và đúng/sai
        multiple_choice_questions = []
        true_false_questions = []
        
        # Số lượng câu hỏi trắc nghiệm và đúng/sai
        num_multiple_choice = num_questions // 2
        num_true_false = num_questions - num_multiple_choice
        
        # Tạo câu hỏi trắc nghiệm
        for i in range(min(num_multiple_choice, len(important_sentences))):
            question = generate_multiple_choice_question(important_sentences[i], important_sentences)
            if question:
                multiple_choice_questions.append(question)
        
        # Tạo câu hỏi đúng/sai
        for i in range(min(num_true_false, len(important_sentences) - len(multiple_choice_questions))):
            index = len(multiple_choice_questions) + i
            if index < len(important_sentences):
                question = generate_true_false_question(important_sentences[index])
                if question:
                    true_false_questions.append(question)
        
        return {
            'multiple_choice': multiple_choice_questions,
            'true_false': true_false_questions
        }
    
    except Exception as e:
        logger.error(f"Lỗi khi tạo bài kiểm tra từ bài học: {e}")
        return {'multiple_choice': [], 'true_false': []}
