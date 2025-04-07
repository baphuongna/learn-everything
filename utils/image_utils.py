import random
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.conf import settings
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

    # Tạo ảnh mới
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Vẽ gradient
    for y in range(height):
        r = int(start_color[0] + (end_color[0] - start_color[0]) * y / height)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * y / height)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Lấy chữ cái đầu tiên của văn bản
    if text:
        initial = text[0].upper()
    else:
        initial = "?"

    # Vẽ chữ cái đầu tiên ở giữa ảnh
    try:
        # Thử tải font mặc định
        font_size = min(width, height) // 2
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        # Nếu không tìm thấy font, sử dụng font mặc định
        font = ImageFont.load_default()

    # Tính toán vị trí để đặt chữ cái ở giữa
    try:
        # Phiên bản mới của Pillow
        text_width, text_height = font.getbbox(initial)[2:]
    except AttributeError:
        try:
            # Phiên bản cũ hơn của Pillow
            text_width, text_height = draw.textsize(initial, font=font)
        except AttributeError:
            # Fallback nếu cả hai phương thức đều không khả dụng
            text_width, text_height = font.getsize(initial)

    position = ((width - text_width) // 2, (height - text_height) // 2)

    # Vẽ chữ cái với màu trắng
    draw.text(position, initial, fill=(255, 255, 255), font=font)

    # Lưu ảnh vào BytesIO
    output = BytesIO()
    image.save(output, format='PNG')
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
