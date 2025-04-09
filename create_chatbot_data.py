"""
Script tạo dữ liệu mẫu cho chatbot.
"""
import os
import django

# Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning_platform.settings')
django.setup()

# Import model
from learning_chatbot.models import ChatbotCategory, ChatbotQuestion

# Tạo danh mục câu hỏi
def create_categories():
    categories = [
        {
            'name': 'Tổng quan về nền tảng',
            'description': 'Các câu hỏi về tổng quan và cách sử dụng nền tảng học tập',
            'order': 1
        },
        {
            'name': 'Tài khoản và đăng nhập',
            'description': 'Các câu hỏi về tài khoản, đăng nhập và bảo mật',
            'order': 2
        },
        {
            'name': 'Nội dung học tập',
            'description': 'Các câu hỏi về nội dung học tập và tài liệu',
            'order': 3
        },
        {
            'name': 'Tính năng học tập',
            'description': 'Các câu hỏi về các tính năng học tập như flashcards, quizzes, v.v.',
            'order': 4
        },
        {
            'name': 'Kỹ thuật',
            'description': 'Các câu hỏi về vấn đề kỹ thuật và hỗ trợ',
            'order': 5
        }
    ]
    
    created_categories = []
    for category_data in categories:
        category, created = ChatbotCategory.objects.get_or_create(
            name=category_data['name'],
            defaults={
                'description': category_data['description'],
                'order': category_data['order'],
                'is_active': True
            }
        )
        created_categories.append(category)
        if created:
            print(f"Đã tạo danh mục: {category.name}")
        else:
            print(f"Danh mục đã tồn tại: {category.name}")
    
    return created_categories

# Tạo câu hỏi thường gặp
def create_questions(categories):
    questions = [
        # Tổng quan về nền tảng
        {
            'category': categories[0],
            'question': 'Nền tảng học tập này là gì?',
            'answer': 'Đây là nền tảng học tập trực tuyến giúp người dùng học tập hiệu quả thông qua các tính năng như flashcards, quizzes, ghi chú, và nhiều công cụ học tập khác. Nền tảng này được thiết kế để hỗ trợ việc học tập liên tục và cá nhân hóa trải nghiệm học tập của người dùng.',
            'keywords': 'nền tảng, học tập, là gì, giới thiệu, tổng quan',
            'order': 1
        },
        {
            'category': categories[0],
            'question': 'Làm thế nào để bắt đầu sử dụng nền tảng?',
            'answer': 'Để bắt đầu sử dụng nền tảng, bạn cần:\n1. Đăng ký tài khoản hoặc đăng nhập nếu đã có tài khoản\n2. Khám phá các chủ đề học tập có sẵn hoặc tạo nội dung học tập của riêng bạn\n3. Sử dụng các công cụ học tập như flashcards, quizzes, ghi chú để học hiệu quả\n4. Theo dõi tiến độ học tập của bạn thông qua các báo cáo và thống kê',
            'keywords': 'bắt đầu, sử dụng, hướng dẫn, mới, làm thế nào',
            'order': 2
        },
        {
            'category': categories[0],
            'question': 'Nền tảng này có những tính năng gì?',
            'answer': 'Nền tảng học tập của chúng tôi có nhiều tính năng hỗ trợ học tập hiệu quả:\n- Flashcards: Tạo và học với thẻ ghi nhớ\n- Quizzes: Kiểm tra kiến thức với các bài kiểm tra\n- Ghi chú: Tạo và quản lý ghi chú học tập\n- Mục tiêu học tập: Đặt và theo dõi mục tiêu học tập\n- Thành tích: Nhận huy hiệu và phần thưởng khi đạt được mục tiêu\n- Trợ lý AI: Hỗ trợ học tập với trí tuệ nhân tạo\n- Chatbot: Trả lời các câu hỏi thường gặp\n- Thông báo: Nhận thông báo về tiến độ học tập\n- Cá nhân hóa: Tùy chỉnh trải nghiệm học tập',
            'keywords': 'tính năng, chức năng, có gì, khả năng',
            'order': 3
        },
        
        # Tài khoản và đăng nhập
        {
            'category': categories[1],
            'question': 'Làm thế nào để đăng ký tài khoản?',
            'answer': 'Để đăng ký tài khoản, bạn cần:\n1. Truy cập trang chủ của nền tảng\n2. Nhấp vào nút "Đăng ký" ở góc trên bên phải\n3. Điền thông tin cá nhân như tên, email, mật khẩu\n4. Xác nhận email của bạn thông qua liên kết được gửi đến email của bạn\n5. Sau khi xác nhận, bạn có thể đăng nhập và bắt đầu sử dụng nền tảng',
            'keywords': 'đăng ký, tài khoản, tạo tài khoản, đăng ký tài khoản',
            'order': 1
        },
        {
            'category': categories[1],
            'question': 'Tôi quên mật khẩu, phải làm sao?',
            'answer': 'Nếu bạn quên mật khẩu, bạn có thể thực hiện các bước sau để đặt lại mật khẩu:\n1. Truy cập trang đăng nhập\n2. Nhấp vào liên kết "Quên mật khẩu"\n3. Nhập email đã đăng ký của bạn\n4. Kiểm tra email của bạn để nhận liên kết đặt lại mật khẩu\n5. Nhấp vào liên kết và tạo mật khẩu mới\n6. Đăng nhập với mật khẩu mới của bạn',
            'keywords': 'quên mật khẩu, đặt lại mật khẩu, reset password, mất mật khẩu',
            'order': 2
        },
        {
            'category': categories[1],
            'question': 'Làm thế nào để thay đổi thông tin cá nhân?',
            'answer': 'Để thay đổi thông tin cá nhân, bạn cần:\n1. Đăng nhập vào tài khoản của bạn\n2. Nhấp vào ảnh đại diện hoặc tên người dùng ở góc trên bên phải\n3. Chọn "Hồ sơ" hoặc "Cài đặt tài khoản"\n4. Cập nhật thông tin cá nhân như tên, ảnh đại diện, email, v.v.\n5. Nhấp vào nút "Lưu" hoặc "Cập nhật" để lưu thay đổi',
            'keywords': 'thay đổi thông tin, cập nhật thông tin, chỉnh sửa hồ sơ, thông tin cá nhân',
            'order': 3
        },
        
        # Nội dung học tập
        {
            'category': categories[2],
            'question': 'Làm thế nào để tìm kiếm nội dung học tập?',
            'answer': 'Để tìm kiếm nội dung học tập, bạn có thể:\n1. Sử dụng thanh tìm kiếm ở đầu trang\n2. Duyệt qua các danh mục chủ đề có sẵn\n3. Sử dụng bộ lọc để thu hẹp kết quả tìm kiếm theo chủ đề, cấp độ, v.v.\n4. Kiểm tra các nội dung được đề xuất dựa trên lịch sử học tập của bạn\n5. Xem các nội dung phổ biến hoặc mới nhất',
            'keywords': 'tìm kiếm, nội dung, học tập, tìm, search',
            'order': 1
        },
        {
            'category': categories[2],
            'question': 'Làm thế nào để tạo nội dung học tập của riêng tôi?',
            'answer': 'Để tạo nội dung học tập của riêng bạn, bạn có thể:\n1. Đăng nhập vào tài khoản của bạn\n2. Truy cập vào phần "Nội dung của tôi" hoặc "Tạo nội dung"\n3. Chọn loại nội dung bạn muốn tạo (bài học, flashcards, quizzes, v.v.)\n4. Điền thông tin và nội dung cần thiết\n5. Lưu và xuất bản nội dung của bạn\n6. Bạn có thể chia sẻ nội dung với người khác hoặc giữ riêng tư',
            'keywords': 'tạo nội dung, nội dung riêng, tự tạo, create content',
            'order': 2
        },
        {
            'category': categories[2],
            'question': 'Tôi có thể chia sẻ nội dung học tập không?',
            'answer': 'Có, bạn có thể chia sẻ nội dung học tập của mình với người khác. Để chia sẻ nội dung:\n1. Truy cập vào nội dung bạn muốn chia sẻ\n2. Nhấp vào nút "Chia sẻ" hoặc biểu tượng chia sẻ\n3. Chọn phương thức chia sẻ (liên kết, email, mạng xã hội, v.v.)\n4. Bạn cũng có thể đặt quyền truy cập cho nội dung (công khai, riêng tư, chỉ với một số người dùng cụ thể)\n5. Người nhận có thể xem hoặc sao chép nội dung tùy thuộc vào quyền bạn đã đặt',
            'keywords': 'chia sẻ, share, nội dung, public, công khai',
            'order': 3
        },
        
        # Tính năng học tập
        {
            'category': categories[3],
            'question': 'Làm thế nào để sử dụng flashcards?',
            'answer': 'Để sử dụng flashcards, bạn có thể:\n1. Truy cập vào phần "Flashcards" từ menu chính\n2. Chọn bộ flashcards có sẵn hoặc tạo bộ mới của riêng bạn\n3. Để tạo bộ mới, nhấp vào "Tạo bộ flashcards" và thêm các thẻ với mặt trước và mặt sau\n4. Để học với flashcards, chọn bộ và nhấp vào "Học ngay"\n5. Lật thẻ để xem câu trả lời và đánh giá mức độ nhớ của bạn\n6. Theo dõi tiến độ học tập của bạn qua thời gian',
            'keywords': 'flashcards, thẻ ghi nhớ, thẻ học, học thẻ',
            'order': 1
        },
        {
            'category': categories[3],
            'question': 'Làm thế nào để tạo và làm bài kiểm tra (quizzes)?',
            'answer': 'Để tạo và làm bài kiểm tra (quizzes), bạn có thể:\n1. Truy cập vào phần "Quizzes" từ menu chính\n2. Để tạo bài kiểm tra mới, nhấp vào "Tạo bài kiểm tra"\n3. Thêm tiêu đề, mô tả và các câu hỏi với nhiều loại (trắc nghiệm, đúng/sai, v.v.)\n4. Lưu và xuất bản bài kiểm tra của bạn\n5. Để làm bài kiểm tra, chọn bài kiểm tra và nhấp vào "Bắt đầu"\n6. Trả lời các câu hỏi và nộp bài để xem kết quả\n7. Xem lại câu trả lời và học từ các lỗi của bạn',
            'keywords': 'quizzes, bài kiểm tra, tạo bài kiểm tra, làm bài kiểm tra, test',
            'order': 2
        },
        {
            'category': categories[3],
            'question': 'Làm thế nào để sử dụng trợ lý học tập AI?',
            'answer': 'Để sử dụng trợ lý học tập AI, bạn có thể:\n1. Truy cập vào phần "Trợ lý AI" từ menu chính\n2. Tạo cuộc trò chuyện mới hoặc tiếp tục cuộc trò chuyện hiện có\n3. Đặt câu hỏi hoặc yêu cầu trợ giúp về nội dung học tập\n4. Trợ lý AI sẽ phản hồi với câu trả lời hoặc hướng dẫn\n5. Bạn có thể liên kết cuộc trò chuyện với chủ đề hoặc bài học cụ thể để nhận câu trả lời phù hợp hơn\n6. Đánh giá câu trả lời để giúp cải thiện trợ lý AI',
            'keywords': 'trợ lý AI, AI, trí tuệ nhân tạo, assistant, chatbot AI',
            'order': 3
        },
        
        # Kỹ thuật
        {
            'category': categories[4],
            'question': 'Tôi gặp lỗi khi sử dụng nền tảng, phải làm sao?',
            'answer': 'Nếu bạn gặp lỗi khi sử dụng nền tảng, bạn có thể thử các cách sau:\n1. Làm mới trang (F5 hoặc Ctrl+R)\n2. Xóa cache và cookie của trình duyệt\n3. Thử sử dụng trình duyệt khác (Chrome, Firefox, Edge, v.v.)\n4. Kiểm tra kết nối internet của bạn\n5. Đăng xuất và đăng nhập lại\n6. Nếu vẫn gặp lỗi, liên hệ với đội hỗ trợ qua phần "Hỗ trợ" hoặc gửi email đến support@learningplatform.com với mô tả chi tiết về lỗi và ảnh chụp màn hình nếu có thể',
            'keywords': 'lỗi, error, bug, vấn đề, không hoạt động, sự cố',
            'order': 1
        },
        {
            'category': categories[4],
            'question': 'Nền tảng có hỗ trợ thiết bị di động không?',
            'answer': 'Có, nền tảng của chúng tôi hỗ trợ đầy đủ cho thiết bị di động. Bạn có thể truy cập nền tảng qua:\n1. Trình duyệt web trên điện thoại hoặc máy tính bảng (trang web đáp ứng)\n2. Ứng dụng di động cho iOS (từ App Store)\n3. Ứng dụng di động cho Android (từ Google Play Store)\n\nTất cả các tính năng chính đều có sẵn trên thiết bị di động, cho phép bạn học tập mọi lúc, mọi nơi.',
            'keywords': 'di động, mobile, điện thoại, tablet, máy tính bảng, app, ứng dụng',
            'order': 2
        },
        {
            'category': categories[4],
            'question': 'Làm thế nào để liên hệ với đội hỗ trợ?',
            'answer': 'Để liên hệ với đội hỗ trợ, bạn có thể:\n1. Sử dụng chatbot hỗ trợ trực tuyến (có sẵn 24/7)\n2. Gửi yêu cầu hỗ trợ qua phần "Hỗ trợ" trong menu chính\n3. Gửi email đến support@learningplatform.com\n4. Kiểm tra phần FAQ hoặc Trung tâm trợ giúp để tìm câu trả lời nhanh\n5. Liên hệ qua mạng xã hội của chúng tôi\n\nĐội hỗ trợ của chúng tôi sẽ phản hồi trong vòng 24 giờ làm việc.',
            'keywords': 'liên hệ, hỗ trợ, support, help, trợ giúp, contact',
            'order': 3
        }
    ]
    
    for question_data in questions:
        question, created = ChatbotQuestion.objects.get_or_create(
            question=question_data['question'],
            category=question_data['category'],
            defaults={
                'answer': question_data['answer'],
                'keywords': question_data['keywords'],
                'order': question_data['order'],
                'is_active': True
            }
        )
        if created:
            print(f"Đã tạo câu hỏi: {question.question}")
        else:
            print(f"Câu hỏi đã tồn tại: {question.question}")

if __name__ == '__main__':
    print("Bắt đầu tạo dữ liệu mẫu cho chatbot...")
    categories = create_categories()
    create_questions(categories)
    print("Hoàn thành tạo dữ liệu mẫu cho chatbot!")
