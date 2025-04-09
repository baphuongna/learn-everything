import random
from io import BytesIO
import numpy as np
import cv2
from django.core.files.base import ContentFile
from django.templatetags.static import static

def generate_gradient_image(text, width=200, height=200, start_color=None, end_color=None):
    """
    Tạo ảnh gradient với chữ cái đầu tiên của văn bản ở giữa.

    Args:
        text (str): Văn bản để lấy chữ cái đầu tiên
        width (int): Chiều rộng của ảnh
        height (int): Chiều cao của ảnh
        start_color (tuple): Màu bắt đầu của gradient (R, G, B)
        end_color (tuple): Màu kết thúc của gradient (R, G, B)

    Returns:
        BytesIO: Đối tượng BytesIO chứa ảnh PNG
    """
    # Nếu không có màu được chỉ định, chọn màu ngẫu nhiên
    if not start_color:
        start_color = (
            random.randint(50, 150),
            random.randint(50, 150),
            random.randint(50, 150)
        )

    if not end_color:
        end_color = (
            min(start_color[0] + 100, 255),
            min(start_color[1] + 100, 255),
            min(start_color[2] + 100, 255)
        )

    # Tạo hình ảnh trống với kích thước chỉ định
    image = np.zeros((height, width, 3), dtype=np.uint8)

    # Tạo gradient
    for y in range(height):
        # Tính toán màu cho mỗi dòng dựa trên tỷ lệ y/height
        ratio = y / height
        color = (
            int(start_color[0] + (end_color[0] - start_color[0]) * ratio),
            int(start_color[1] + (end_color[1] - start_color[1]) * ratio),
            int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        )
        # Điền màu cho toàn bộ dòng
        image[y, :] = color

    # Lấy chữ cái đầu tiên của văn bản
    if text:
        initial = text[0].upper()
    else:
        initial = "?"

    # Tính toán kích thước font dựa trên kích thước hình ảnh
    font_size = min(width, height) // 3
    font_scale = font_size / 30  # Điều chỉnh tỷ lệ font cho phù hợp với OpenCV
    font_thickness = max(1, font_size // 20)

    # Tính toán kích thước văn bản để đặt ở giữa
    text_size = cv2.getTextSize(initial, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
    text_x = (width - text_size[0]) // 2
    text_y = (height + text_size[1]) // 2

    # Thêm chữ cái vào giữa hình ảnh
    cv2.putText(image, initial, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX,
                font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

    # Chuyển đổi hình ảnh sang dạng PNG và lưu vào BytesIO
    _, buffer = cv2.imencode('.png', image)
    output = BytesIO(buffer)
    output.seek(0)

    return output

def generate_subject_image(subject):
    """
    Tạo ảnh mặc định cho chủ đề.

    Args:
        subject: Đối tượng Subject

    Returns:
        ContentFile: Đối tượng ContentFile chứa ảnh PNG
    """
    # Tạo ảnh gradient với chữ cái đầu tiên của tên chủ đề
    image_io = generate_gradient_image(subject.name)

    # Tạo tên file
    filename = f"subject_{subject.id}_default.png"

    # Trả về ContentFile để lưu vào ImageField
    return ContentFile(image_io.getvalue(), name=filename)

def generate_profile_image(user_profile):
    """
    Tạo ảnh mặc định cho hồ sơ người dùng.

    Args:
        user_profile: Đối tượng UserProfile

    Returns:
        ContentFile: Đối tượng ContentFile chứa ảnh PNG
    """
    # Lấy tên người dùng
    if user_profile.user.first_name:
        name = user_profile.user.first_name
    else:
        name = user_profile.user.username

    # Tạo ảnh gradient với chữ cái đầu tiên của tên người dùng
    image_io = generate_gradient_image(name)

    # Tạo tên file
    filename = f"profile_{user_profile.user.id}_default.png"

    # Trả về ContentFile để lưu vào ImageField
    return ContentFile(image_io.getvalue(), name=filename)

def ensure_subject_image(subject):
    """
    Đảm bảo chủ đề có ảnh. Nếu không có, tạo ảnh mặc định.

    Args:
        subject: Đối tượng Subject
    """
    if not subject.icon:
        subject.icon = generate_subject_image(subject)
        subject.save(update_fields=['icon'])

def generate_lesson_image(lesson):
    """
    Tạo ảnh mặc định cho bài học.

    Args:
        lesson: Đối tượng Lesson

    Returns:
        ContentFile: Đối tượng ContentFile chứa ảnh PNG
    """
    # Tạo ảnh gradient với chữ cái đầu tiên của tên bài học
    # Sử dụng màu xanh lá cây cho bài học
    image_io = generate_gradient_image(lesson.title, start_color=(50, 150, 50))

    # Tạo tên file
    filename = f"lesson_{lesson.id}_default.png"

    # Trả về ContentFile để lưu vào ImageField
    return ContentFile(image_io.getvalue(), name=filename)

def generate_flashcard_image(flashcard):
    """
    Tạo ảnh mặc định cho flashcard.

    Args:
        flashcard: Đối tượng Flashcard

    Returns:
        ContentFile: Đối tượng ContentFile chứa ảnh PNG
    """
    # Tạo ảnh gradient với chữ cái đầu tiên của mặt trước flashcard
    # Sử dụng màu cam cho flashcard
    image_io = generate_gradient_image(flashcard.front, start_color=(200, 100, 50))

    # Tạo tên file
    filename = f"flashcard_{flashcard.id}_default.png"

    # Trả về ContentFile để lưu vào ImageField
    return ContentFile(image_io.getvalue(), name=filename)

def ensure_profile_image(user_profile):
    """
    Đảm bảo hồ sơ người dùng có ảnh. Nếu không có, tạo ảnh mặc định.

    Args:
        user_profile: Đối tượng UserProfile
    """
    if not user_profile.avatar:
        user_profile.avatar = generate_profile_image(user_profile)
        user_profile.save(update_fields=['avatar'])

def ensure_lesson_image(lesson):
    """
    Đảm bảo bài học có ảnh. Nếu không có, tạo ảnh mặc định.

    Args:
        lesson: Đối tượng Lesson
    """
    if not lesson.image:
        lesson.image = generate_lesson_image(lesson)
        lesson.save(update_fields=['image'])

def ensure_flashcard_image(flashcard):
    """
    Đảm bảo flashcard có ảnh. Nếu không có, tạo ảnh mặc định.

    Args:
        flashcard: Đối tượng Flashcard
    """
    if not flashcard.image:
        flashcard.image = generate_flashcard_image(flashcard)
        flashcard.save(update_fields=['image'])

# Danh sách các biểu tượng chủ đề có sẵn
SUBJECT_ICONS = {
    'python': 'images/subject_icons/python.svg',
    'java': 'images/subject_icons/java.svg',
    'javascript': 'images/subject_icons/javascript.svg',
    'english': 'images/subject_icons/english.svg',
    'chinese': 'images/subject_icons/chinese.svg',
    'math': 'images/subject_icons/math.svg',
}

def get_subject_icon_url(subject_name):
    """
    Lấy URL của biểu tượng chủ đề dựa trên tên chủ đề.

    Args:
        subject_name: Tên chủ đề

    Returns:
        str: URL của biểu tượng chủ đề
    """
    # Chuyển tên chủ đề thành chữ thường và loại bỏ khoảng trắng
    key = subject_name.lower().replace(' ', '')

    # Kiểm tra xem có biểu tượng phù hợp không
    if key in SUBJECT_ICONS:
        return static(SUBJECT_ICONS[key])

    # Nếu không có biểu tượng phù hợp, trả về None
    return None

def update_subject_with_icon(subject):
    """
    Cập nhật chủ đề với biểu tượng đẹp.

    Args:
        subject: Đối tượng Subject
    """
    # Kiểm tra xem chủ đề đã có biểu tượng chưa
    if not subject.icon:
        # Lấy URL của biểu tượng chủ đề
        icon_url = get_subject_icon_url(subject.name)

        if icon_url:
            # Nếu có biểu tượng phù hợp, sử dụng nó
            # TODO: Cập nhật chủ đề với biểu tượng đẹp
            # Hiện tại, chúng ta vẫn sử dụng hàm generate_subject_image
            ensure_subject_image(subject)
        else:
            # Nếu không có biểu tượng phù hợp, sử dụng hàm generate_subject_image
            ensure_subject_image(subject)
