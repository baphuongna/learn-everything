import os
import django
import datetime

# Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning_platform.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from content.models import Subject, Topic, Lesson
from flashcards.models import FlashcardSet, Flashcard
from quizzes.models import Quiz, Question, Answer

def create_sample_data():
    # Tạo chủ đề
    python_subject = Subject.objects.create(
        name='Python',
        description='Học lập trình Python từ cơ bản đến nâng cao.',
        slug='python'
    )
    
    english_subject = Subject.objects.create(
        name='Tiếng Anh',
        description='Học tiếng Anh với các bài học từ vựng, ngữ pháp và luyện phát âm.',
        slug='tieng-anh'
    )
    
    math_subject = Subject.objects.create(
        name='Toán Học',
        description='Học toán với phương pháp Kumon, từ đại số đến giải tích và hình học.',
        slug='toan-hoc'
    )
    
    chinese_subject = Subject.objects.create(
        name='Tiếng Trung',
        description='Học tiếng Trung với các bài học từ vựng, ngữ pháp và luyện phát âm.',
        slug='tieng-trung'
    )
    
    # Tạo chủ đề con cho Python
    python_basics = Topic.objects.create(
        subject=python_subject,
        name='Cơ Bản Python',
        description='Học các khái niệm cơ bản của Python như biến, kiểu dữ liệu, và cấu trúc điều khiển.',
        slug='co-ban-python',
        order=1
    )
    
    python_oop = Topic.objects.create(
        subject=python_subject,
        name='Lập Trình Hướng Đối Tượng',
        description='Học về lập trình hướng đối tượng trong Python với các khái niệm như lớp, đối tượng, kế thừa, và đa hình.',
        slug='lap-trinh-huong-doi-tuong',
        order=2
    )
    
    # Tạo bài học cho Python cơ bản
    lesson1 = Lesson.objects.create(
        topic=python_basics,
        title='Biến và Kiểu Dữ Liệu',
        content="""
# Biến và Kiểu Dữ Liệu trong Python

Python là một ngôn ngữ lập trình động, có nghĩa là bạn không cần khai báo kiểu dữ liệu khi tạo biến. Python sẽ tự động xác định kiểu dữ liệu dựa trên giá trị được gán.

## Tạo Biến

Trong Python, bạn có thể tạo biến bằng cách gán giá trị cho nó:

```python
x = 5       # Số nguyên
y = 3.14    # Số thực
name = "Python"  # Chuỗi
is_valid = True  # Boolean
```

## Các Kiểu Dữ Liệu Cơ Bản

Python có các kiểu dữ liệu cơ bản sau:

1. **Số nguyên (int)**: Ví dụ: 1, 100, -10
2. **Số thực (float)**: Ví dụ: 3.14, -0.001, 2.0
3. **Chuỗi (str)**: Ví dụ: "Hello", 'Python'
4. **Boolean (bool)**: True hoặc False
5. **None**: Đại diện cho "không có giá trị"

## Kiểm Tra Kiểu Dữ Liệu

Bạn có thể sử dụng hàm `type()` để kiểm tra kiểu dữ liệu của một biến:

```python
x = 5
print(type(x))  # <class 'int'>

y = "Hello"
print(type(y))  # <class 'str'>
```

## Chuyển Đổi Kiểu Dữ Liệu

Python cung cấp các hàm để chuyển đổi giữa các kiểu dữ liệu:

```python
# Chuyển đổi sang số nguyên
x = int(3.14)    # x = 3
y = int("10")    # y = 10

# Chuyển đổi sang số thực
a = float(5)     # a = 5.0
b = float("3.14") # b = 3.14

# Chuyển đổi sang chuỗi
s = str(42)      # s = "42"
```

## Bài Tập Thực Hành

1. Tạo các biến với các kiểu dữ liệu khác nhau
2. Sử dụng hàm `type()` để kiểm tra kiểu dữ liệu
3. Thực hiện các phép chuyển đổi kiểu dữ liệu
""",
        slug='bien-va-kieu-du-lieu',
        order=1
    )
    
    lesson2 = Lesson.objects.create(
        topic=python_basics,
        title='Cấu Trúc Điều Khiển',
        content="""
# Cấu Trúc Điều Khiển trong Python

Cấu trúc điều khiển cho phép bạn kiểm soát luồng thực thi của chương trình. Python cung cấp các cấu trúc điều khiển như câu lệnh điều kiện và vòng lặp.

## Câu Lệnh Điều Kiện

### Câu lệnh if-else

```python
x = 10

if x > 0:
    print("x là số dương")
elif x < 0:
    print("x là số âm")
else:
    print("x bằng 0")
```

### Toán tử ba ngôi

```python
x = 10
result = "Dương" if x > 0 else "Không dương"
print(result)  # Dương
```

## Vòng Lặp

### Vòng lặp for

```python
# Lặp qua một dãy số
for i in range(5):
    print(i)  # In ra 0, 1, 2, 3, 4

# Lặp qua một chuỗi
for char in "Python":
    print(char)  # In ra từng ký tự: P, y, t, h, o, n

# Lặp qua một danh sách
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)
```

### Vòng lặp while

```python
count = 0
while count < 5:
    print(count)
    count += 1  # Tăng count lên 1
```

## Câu Lệnh break và continue

### break

Câu lệnh `break` được sử dụng để thoát khỏi vòng lặp:

```python
for i in range(10):
    if i == 5:
        break
    print(i)  # In ra 0, 1, 2, 3, 4
```

### continue

Câu lệnh `continue` được sử dụng để bỏ qua phần còn lại của vòng lặp hiện tại và tiếp tục với vòng lặp tiếp theo:

```python
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)  # In ra các số lẻ: 1, 3, 5, 7, 9
```

## Bài Tập Thực Hành

1. Viết chương trình kiểm tra một số là chẵn hay lẻ
2. Viết chương trình in ra các số từ 1 đến 10 sử dụng vòng lặp for
3. Viết chương trình in ra các số từ 1 đến 10 sử dụng vòng lặp while
4. Viết chương trình in ra các số chia hết cho 3 trong khoảng từ 1 đến 20
""",
        slug='cau-truc-dieu-khien',
        order=2
    )
    
    # Tạo bài học cho Python OOP
    lesson3 = Lesson.objects.create(
        topic=python_oop,
        title='Lớp và Đối Tượng',
        content="""
# Lớp và Đối Tượng trong Python

Lập trình hướng đối tượng (OOP) là một phương pháp lập trình dựa trên khái niệm về "đối tượng", có thể chứa dữ liệu và mã. Python hỗ trợ đầy đủ lập trình hướng đối tượng.

## Định Nghĩa Lớp

Một lớp là một bản thiết kế cho đối tượng. Bạn có thể định nghĩa một lớp bằng từ khóa `class`:

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def say_hello(self):
        print(f"Xin chào, tôi là {self.name} và tôi {self.age} tuổi.")
```

Trong ví dụ trên:
- `__init__` là một phương thức đặc biệt được gọi khi tạo một đối tượng mới.
- `self` đại diện cho đối tượng hiện tại.
- `name` và `age` là các thuộc tính của đối tượng.
- `say_hello` là một phương thức của lớp.

## Tạo Đối Tượng

Sau khi định nghĩa lớp, bạn có thể tạo các đối tượng từ lớp đó:

```python
# Tạo đối tượng Person
person1 = Person("Alice", 30)
person2 = Person("Bob", 25)

# Gọi phương thức
person1.say_hello()  # Xin chào, tôi là Alice và tôi 30 tuổi.
person2.say_hello()  # Xin chào, tôi là Bob và tôi 25 tuổi.
```

## Thuộc Tính và Phương Thức

- **Thuộc tính**: Biến thuộc về một đối tượng.
- **Phương thức**: Hàm thuộc về một đối tượng.

```python
# Truy cập thuộc tính
print(person1.name)  # Alice
print(person1.age)   # 30

# Thay đổi thuộc tính
person1.age = 31
print(person1.age)   # 31
```

## Thuộc Tính và Phương Thức Tĩnh

- **Thuộc tính tĩnh**: Thuộc về lớp, không phải đối tượng.
- **Phương thức tĩnh**: Không cần truy cập vào thuộc tính của đối tượng.

```python
class MathUtils:
    PI = 3.14159  # Thuộc tính tĩnh
    
    @staticmethod
    def add(a, b):  # Phương thức tĩnh
        return a + b

# Sử dụng thuộc tính và phương thức tĩnh
print(MathUtils.PI)       # 3.14159
print(MathUtils.add(5, 3))  # 8
```

## Bài Tập Thực Hành

1. Tạo một lớp `Rectangle` với các thuộc tính `width` và `height`, và các phương thức để tính diện tích và chu vi.
2. Tạo một lớp `BankAccount` với các thuộc tính `account_number`, `owner`, và `balance`, và các phương thức để gửi và rút tiền.
3. Tạo một lớp `Student` với các thuộc tính `name`, `age`, và `grades` (danh sách điểm), và các phương thức để tính điểm trung bình và kiểm tra đậu/rớt.
""",
        slug='lop-va-doi-tuong',
        order=1
    )
    
    # Tạo chủ đề con cho Tiếng Anh
    english_vocabulary = Topic.objects.create(
        subject=english_subject,
        name='Từ Vựng',
        description='Học từ vựng tiếng Anh theo chủ đề.',
        slug='tu-vung',
        order=1
    )
    
    english_grammar = Topic.objects.create(
        subject=english_subject,
        name='Ngữ Pháp',
        description='Học ngữ pháp tiếng Anh từ cơ bản đến nâng cao.',
        slug='ngu-phap',
        order=2
    )
    
    # Tạo bài học cho Tiếng Anh
    lesson4 = Lesson.objects.create(
        topic=english_vocabulary,
        title='Từ Vựng Về Gia Đình',
        content="""
# Từ Vựng Về Gia Đình

Trong bài học này, chúng ta sẽ học các từ vựng tiếng Anh liên quan đến gia đình.

## Các Thành Viên Trong Gia Đình

| Tiếng Anh | Tiếng Việt |
|-----------|------------|
| Father    | Cha        |
| Mother    | Mẹ         |
| Son       | Con trai   |
| Daughter  | Con gái    |
| Brother   | Anh/Em trai|
| Sister    | Chị/Em gái |
| Grandfather | Ông      |
| Grandmother | Bà       |
| Uncle     | Chú/Bác    |
| Aunt      | Cô/Dì      |
| Cousin    | Anh/Chị/Em họ |
| Nephew    | Cháu trai  |
| Niece     | Cháu gái   |
| Husband   | Chồng      |
| Wife      | Vợ         |
| Parents   | Bố mẹ      |
| Children  | Con cái    |
| Siblings  | Anh chị em |
| Family    | Gia đình   |

## Ví Dụ Câu

1. This is my **father**. (Đây là **cha** tôi.)
2. My **mother** is a teacher. (**Mẹ** tôi là một giáo viên.)
3. I have two **brothers** and one **sister**. (Tôi có hai **anh/em trai** và một **chị/em gái**.)
4. My **grandparents** live in the countryside. (**Ông bà** tôi sống ở nông thôn.)
5. We are a happy **family**. (Chúng tôi là một **gia đình** hạnh phúc.)

## Bài Tập

1. Hoàn thành các câu sau với từ vựng phù hợp:
   - My _______ is my father's father.
   - My _______ is my mother's sister.
   - My _______ is my uncle's son.
   - My _______ are my father and mother.

2. Viết một đoạn văn ngắn giới thiệu về gia đình của bạn bằng tiếng Anh.

3. Vẽ sơ đồ gia đình của bạn và ghi nhãn các thành viên bằng tiếng Anh.
""",
        slug='tu-vung-ve-gia-dinh',
        order=1
    )
    
    # Tạo flashcard set cho bài học Python
    python_variables_flashcards = FlashcardSet.objects.create(
        lesson=lesson1,
        title='Flashcards Biến và Kiểu Dữ Liệu',
        description='Ôn tập các khái niệm về biến và kiểu dữ liệu trong Python.'
    )
    
    # Tạo các flashcard
    Flashcard.objects.create(
        flashcard_set=python_variables_flashcards,
        front='int',
        back='Kiểu dữ liệu số nguyên trong Python. Ví dụ: 1, 100, -10'
    )
    
    Flashcard.objects.create(
        flashcard_set=python_variables_flashcards,
        front='float',
        back='Kiểu dữ liệu số thực trong Python. Ví dụ: 3.14, -0.001, 2.0'
    )
    
    Flashcard.objects.create(
        flashcard_set=python_variables_flashcards,
        front='str',
        back='Kiểu dữ liệu chuỗi trong Python. Ví dụ: "Hello", \'Python\''
    )
    
    Flashcard.objects.create(
        flashcard_set=python_variables_flashcards,
        front='bool',
        back='Kiểu dữ liệu Boolean trong Python. Giá trị: True hoặc False'
    )
    
    Flashcard.objects.create(
        flashcard_set=python_variables_flashcards,
        front='type()',
        back='Hàm để kiểm tra kiểu dữ liệu của một biến trong Python'
    )
    
    # Tạo flashcard set cho bài học Tiếng Anh
    english_family_flashcards = FlashcardSet.objects.create(
        lesson=lesson4,
        title='Flashcards Từ Vựng Gia Đình',
        description='Ôn tập từ vựng tiếng Anh về gia đình.'
    )
    
    # Tạo các flashcard tiếng Anh
    Flashcard.objects.create(
        flashcard_set=english_family_flashcards,
        front='Father',
        back='Cha'
    )
    
    Flashcard.objects.create(
        flashcard_set=english_family_flashcards,
        front='Mother',
        back='Mẹ'
    )
    
    Flashcard.objects.create(
        flashcard_set=english_family_flashcards,
        front='Brother',
        back='Anh/Em trai'
    )
    
    Flashcard.objects.create(
        flashcard_set=english_family_flashcards,
        front='Sister',
        back='Chị/Em gái'
    )
    
    Flashcard.objects.create(
        flashcard_set=english_family_flashcards,
        front='Grandfather',
        back='Ông'
    )
    
    # Tạo quiz cho bài học Python
    python_variables_quiz = Quiz.objects.create(
        lesson=lesson1,
        title='Kiểm Tra Biến và Kiểu Dữ Liệu',
        description='Kiểm tra kiến thức về biến và kiểu dữ liệu trong Python.',
        time_limit=10,
        pass_score=70
    )
    
    # Tạo câu hỏi và đáp án
    question1 = Question.objects.create(
        quiz=python_variables_quiz,
        question_text='Kiểu dữ liệu nào được sử dụng để lưu trữ số nguyên trong Python?',
        question_type='single',
        order=1
    )
    
    Answer.objects.create(question=question1, answer_text='int', is_correct=True)
    Answer.objects.create(question=question1, answer_text='float', is_correct=False)
    Answer.objects.create(question=question1, answer_text='str', is_correct=False)
    Answer.objects.create(question=question1, answer_text='bool', is_correct=False)
    
    question2 = Question.objects.create(
        quiz=python_variables_quiz,
        question_text='Đâu là cách khai báo biến đúng trong Python?',
        question_type='multiple',
        order=2
    )
    
    Answer.objects.create(question=question2, answer_text='x = 5', is_correct=True)
    Answer.objects.create(question=question2, answer_text='int x = 5', is_correct=False)
    Answer.objects.create(question=question2, answer_text='name = "John"', is_correct=True)
    Answer.objects.create(question=question2, answer_text='string name = "John"', is_correct=False)
    
    question3 = Question.objects.create(
        quiz=python_variables_quiz,
        question_text='Hàm nào được sử dụng để kiểm tra kiểu dữ liệu của một biến trong Python?',
        question_type='single',
        order=3
    )
    
    Answer.objects.create(question=question3, answer_text='type()', is_correct=True)
    Answer.objects.create(question=question3, answer_text='typeof()', is_correct=False)
    Answer.objects.create(question=question3, answer_text='datatype()', is_correct=False)
    Answer.objects.create(question=question3, answer_text='check_type()', is_correct=False)
    
    # Tạo quiz cho bài học Tiếng Anh
    english_family_quiz = Quiz.objects.create(
        lesson=lesson4,
        title='Kiểm Tra Từ Vựng Gia Đình',
        description='Kiểm tra kiến thức về từ vựng tiếng Anh về gia đình.',
        time_limit=5,
        pass_score=80
    )
    
    # Tạo câu hỏi và đáp án
    question4 = Question.objects.create(
        quiz=english_family_quiz,
        question_text='Từ nào trong tiếng Anh có nghĩa là "Cha"?',
        question_type='single',
        order=1
    )
    
    Answer.objects.create(question=question4, answer_text='Father', is_correct=True)
    Answer.objects.create(question=question4, answer_text='Mother', is_correct=False)
    Answer.objects.create(question=question4, answer_text='Brother', is_correct=False)
    Answer.objects.create(question=question4, answer_text='Son', is_correct=False)
    
    question5 = Question.objects.create(
        quiz=english_family_quiz,
        question_text='Chọn các từ chỉ thành viên trong gia đình:',
        question_type='multiple',
        order=2
    )
    
    Answer.objects.create(question=question5, answer_text='Sister', is_correct=True)
    Answer.objects.create(question=question5, answer_text='Teacher', is_correct=False)
    Answer.objects.create(question=question5, answer_text='Uncle', is_correct=True)
    Answer.objects.create(question=question5, answer_text='Friend', is_correct=False)
    
    print("Đã tạo dữ liệu mẫu thành công!")

if __name__ == '__main__':
    create_sample_data()
