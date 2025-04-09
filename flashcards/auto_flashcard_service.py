import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from django.conf import settings
import requests
import json

# Đảm bảo NLTK đã tải các dữ liệu cần thiết
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')


class AutoFlashcardService:
    """
    Dịch vụ tự động tạo flashcard từ văn bản
    """
    
    def __init__(self):
        self.openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.openai_model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
        
        # Khởi tạo các công cụ NLP
        self.lemmatizer = WordNetLemmatizer()
        self.stopwords = set(stopwords.words('english'))
        
        # Thêm stopwords tiếng Việt
        self.vietnamese_stopwords = self._load_vietnamese_stopwords()
    
    def _load_vietnamese_stopwords(self):
        """Tải danh sách stopwords tiếng Việt"""
        vietnamese_stopwords = set([
            "và", "của", "cho", "là", "để", "trong", "được", "với", "có", "không",
            "những", "một", "các", "về", "như", "này", "từ", "khi", "đến", "người",
            "thì", "năm", "vào", "ra", "còn", "bị", "đã", "sẽ", "phải", "nên",
            "đây", "lúc", "vì", "cũng", "nếu", "trên", "dưới", "theo", "đó", "tại",
            "nhưng", "mà", "vẫn", "làm", "sau", "rồi", "thế", "lên", "xuống", "ngoài",
            "quá", "rất", "mới", "đang", "cần", "muốn", "thêm", "chỉ", "bởi", "vậy"
        ])
        return vietnamese_stopwords
    
    def extract_key_terms(self, text, language='en', max_terms=10):
        """
        Trích xuất các thuật ngữ quan trọng từ văn bản
        
        Args:
            text: Văn bản đầu vào
            language: Ngôn ngữ ('en' hoặc 'vi')
            max_terms: Số lượng thuật ngữ tối đa
            
        Returns:
            list: Danh sách các thuật ngữ quan trọng
        """
        if not text:
            return []
        
        # Chọn stopwords dựa trên ngôn ngữ
        if language == 'vi':
            stop_words = self.vietnamese_stopwords
        else:
            stop_words = self.stopwords
        
        # Tokenize văn bản
        words = word_tokenize(text.lower())
        
        # Loại bỏ stopwords và ký tự đặc biệt
        words = [word for word in words if word.isalnum() and word not in stop_words]
        
        # Lemmatize (chỉ áp dụng cho tiếng Anh)
        if language == 'en':
            words = [self.lemmatizer.lemmatize(word) for word in words]
        
        # Đếm tần suất
        word_freq = {}
        for word in words:
            if word in word_freq:
                word_freq[word] += 1
            else:
                word_freq[word] = 1
        
        # Sắp xếp theo tần suất và lấy các thuật ngữ hàng đầu
        sorted_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        top_terms = [term for term, freq in sorted_terms[:max_terms]]
        
        return top_terms
    
    def extract_definitions(self, text, terms, language='en'):
        """
        Trích xuất định nghĩa cho các thuật ngữ từ văn bản
        
        Args:
            text: Văn bản đầu vào
            terms: Danh sách các thuật ngữ cần tìm định nghĩa
            language: Ngôn ngữ ('en' hoặc 'vi')
            
        Returns:
            dict: Từ điển các thuật ngữ và định nghĩa
        """
        if not text or not terms:
            return {}
        
        # Tách văn bản thành các câu
        sentences = sent_tokenize(text)
        
        # Tìm các câu chứa thuật ngữ
        term_definitions = {}
        for term in terms:
            term_sentences = []
            for sentence in sentences:
                if re.search(r'\b' + re.escape(term) + r'\b', sentence.lower()):
                    term_sentences.append(sentence)
            
            if term_sentences:
                # Sử dụng câu đầu tiên chứa thuật ngữ làm định nghĩa
                term_definitions[term] = term_sentences[0]
        
        # Nếu không tìm thấy định nghĩa cho một số thuật ngữ, sử dụng AI để tạo
        missing_terms = [term for term in terms if term not in term_definitions]
        if missing_terms and self.openai_api_key:
            ai_definitions = self._generate_definitions_with_ai(missing_terms, text, language)
            term_definitions.update(ai_definitions)
        
        return term_definitions
    
    def _generate_definitions_with_ai(self, terms, context, language='en'):
        """
        Sử dụng OpenAI API để tạo định nghĩa cho các thuật ngữ
        
        Args:
            terms: Danh sách các thuật ngữ cần định nghĩa
            context: Văn bản ngữ cảnh
            language: Ngôn ngữ ('en' hoặc 'vi')
            
        Returns:
            dict: Từ điển các thuật ngữ và định nghĩa
        """
        if not self.openai_api_key or not terms:
            return {}
        
        try:
            # Chuẩn bị prompt
            lang_text = "tiếng Việt" if language == 'vi' else "English"
            terms_str = ", ".join(terms)
            
            prompt = f"""
            Dựa trên văn bản sau, hãy cung cấp định nghĩa ngắn gọn cho các thuật ngữ sau bằng {lang_text}.
            Mỗi định nghĩa chỉ nên là một câu ngắn gọn, súc tích.
            
            Văn bản: {context[:1000]}...
            
            Các thuật ngữ cần định nghĩa: {terms_str}
            
            Định dạng phản hồi:
            thuật_ngữ_1: định nghĩa_1
            thuật_ngữ_2: định nghĩa_2
            ...
            """
            
            # Gọi API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            data = {
                "model": self.openai_model,
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
                definitions_text = result["choices"][0]["message"]["content"].strip()
                
                # Phân tích kết quả
                definitions = {}
                for line in definitions_text.split('\n'):
                    if ':' in line:
                        term, definition = line.split(':', 1)
                        term = term.strip().lower()
                        definition = definition.strip()
                        if term in terms:
                            definitions[term] = definition
                
                return definitions
            else:
                return {}
        except Exception as e:
            print(f"Lỗi khi tạo định nghĩa với AI: {str(e)}")
            return {}
    
    def generate_flashcards(self, text, language='en', max_cards=10):
        """
        Tạo flashcards từ văn bản
        
        Args:
            text: Văn bản đầu vào
            language: Ngôn ngữ ('en' hoặc 'vi')
            max_cards: Số lượng flashcard tối đa
            
        Returns:
            list: Danh sách các flashcard (từ khóa, định nghĩa)
        """
        # Trích xuất các thuật ngữ quan trọng
        key_terms = self.extract_key_terms(text, language, max_cards)
        
        # Trích xuất định nghĩa
        definitions = self.extract_definitions(text, key_terms, language)
        
        # Tạo flashcards
        flashcards = []
        for term in key_terms:
            if term in definitions:
                flashcards.append({
                    'front': term,
                    'back': definitions[term]
                })
        
        return flashcards
    
    def generate_flashcards_with_ai(self, text, language='en', max_cards=10):
        """
        Tạo flashcards từ văn bản sử dụng AI
        
        Args:
            text: Văn bản đầu vào
            language: Ngôn ngữ ('en' hoặc 'vi')
            max_cards: Số lượng flashcard tối đa
            
        Returns:
            list: Danh sách các flashcard (từ khóa, định nghĩa)
        """
        if not self.openai_api_key:
            return self.generate_flashcards(text, language, max_cards)
        
        try:
            # Chuẩn bị prompt
            lang_text = "tiếng Việt" if language == 'vi' else "English"
            
            prompt = f"""
            Tạo {max_cards} flashcard từ văn bản sau bằng {lang_text}. 
            Mỗi flashcard nên có mặt trước là một thuật ngữ hoặc khái niệm quan trọng, 
            và mặt sau là định nghĩa hoặc giải thích ngắn gọn.
            
            Văn bản: {text[:2000]}...
            
            Định dạng phản hồi:
            [
              {{"front": "thuật_ngữ_1", "back": "định nghĩa_1"}},
              {{"front": "thuật_ngữ_2", "back": "định nghĩa_2"}},
              ...
            ]
            """
            
            # Gọi API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            data = {
                "model": self.openai_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # Trích xuất phần JSON
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    try:
                        flashcards = json.loads(json_str)
                        return flashcards[:max_cards]
                    except json.JSONDecodeError:
                        pass
            
            # Nếu có lỗi, sử dụng phương pháp không AI
            return self.generate_flashcards(text, language, max_cards)
        
        except Exception as e:
            print(f"Lỗi khi tạo flashcards với AI: {str(e)}")
            return self.generate_flashcards(text, language, max_cards)
