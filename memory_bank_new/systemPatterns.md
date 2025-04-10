# System Patterns - Nền Tảng Học Tập

## Kiến trúc hệ thống
Nền Tảng Học Tập được xây dựng theo mô hình MTV (Model-Template-View) của Django, một biến thể của mô hình MVC (Model-View-Controller) truyền thống.

```
flowchart TD
    Client[Client Browser] <--> Views[Django Views]
    Views <--> Templates[Django Templates]
    Views <--> Models[Django Models]
    Models <--> Database[(PostgreSQL/Supabase)]
    Templates --> HTMX[HTMX]
    Templates --> AlpineJS[Alpine.js]
    Templates --> Bootstrap[Bootstrap]
```

### Các thành phần chính
1. **Models**: Định nghĩa cấu trúc dữ liệu và logic nghiệp vụ
2. **Templates**: Hiển thị dữ liệu và giao diện người dùng
3. **Views**: Xử lý yêu cầu HTTP và điều khiển luồng dữ liệu
4. **URLs**: Định tuyến các yêu cầu đến views tương ứng
5. **Forms**: Xử lý dữ liệu đầu vào từ người dùng
6. **Middleware**: Xử lý các yêu cầu/phản hồi trước/sau khi đến views
7. **Signals**: Xử lý các sự kiện trong hệ thống

## Cấu trúc ứng dụng
Dự án được tổ chức thành nhiều ứng dụng Django, mỗi ứng dụng đảm nhận một chức năng cụ thể:

```
flowchart TD
    Core[learning_platform] --> Accounts[accounts]
    Core --> Content[content]
    Core --> Flashcards[flashcards]
    Core --> Quizzes[quizzes]
    Core --> MemoryBank[memory_bank]
    Core --> AdvancedLearning[advanced_learning]
    Core --> Notifications[notifications]
    Core --> LearningGoals[learning_goals]
    Core --> Achievements[achievements]
    Core --> Personalization[personalization]
    Core --> AIAssistant[ai_assistant]
    Core --> LearningChatbot[learning_chatbot]
    Core --> LearningAnalytics[learning_analytics]
    Core --> OCRApp[ocr_app]
    Core --> NoteIntegration[note_integration_app]
```

### Mô tả các ứng dụng
1. **accounts**: Quản lý người dùng, xác thực và hồ sơ
2. **content**: Quản lý nội dung học tập (chủ đề, bài học)
3. **flashcards**: Hệ thống flashcards và spaced repetition
4. **quizzes**: Bài kiểm tra và đánh giá
5. **memory_bank**: Lưu trữ và quản lý ghi nhớ
6. **advanced_learning**: Các phương pháp học tập nâng cao
7. **notifications**: Hệ thống thông báo
8. **learning_goals**: Quản lý mục tiêu học tập
9. **achievements**: Hệ thống thành tích và phần thưởng
10. **personalization**: Cá nhân hóa trải nghiệm học tập
11. **ai_assistant**: Trợ lý học tập AI
12. **learning_chatbot**: Chatbot hỗ trợ học tập
13. **learning_analytics**: Phân tích dữ liệu học tập
14. **ocr_app**: Nhận dạng ký tự quang học
15. **note_integration_app**: Tích hợp công cụ ghi chú

## Mô hình dữ liệu
Các mô hình dữ liệu chính trong hệ thống:

```
flowchart TD
    User[User] --> UserProfile[UserProfile]
    User --> LearningGoal[LearningGoal]
    User --> DailyStudyLog[DailyStudyLog]
    
    Subject[Subject] --> Topic[Topic]
    Topic --> Lesson[Lesson]
    
    User --> Flashcard[Flashcard]
    User --> FlashcardDeck[FlashcardDeck]
    FlashcardDeck --> Flashcard
    
    User --> Quiz[Quiz]
    Quiz --> Question[Question]
    Question --> Answer[Answer]
    
    User --> PomodoroSession[PomodoroSession]
    User --> CornellNote[CornellNote]
    User --> MindMap[MindMap]
    User --> FeynmanNote[FeynmanNote]
    
    User --> Project[Project]
    Project --> ProjectTask[ProjectTask]
    User --> UserProject[UserProject]
    UserProject --> Project
    
    User --> InteractiveExercise[InteractiveExercise]
    User --> CompetitionMode[CompetitionMode]
    CompetitionMode --> CompetitionQuestion[CompetitionQuestion]
    
    User --> Notification[Notification]
    User --> Achievement[Achievement]
    User --> UserAchievement[UserAchievement]
```

## Các mẫu thiết kế
### Mẫu Repository
Sử dụng Django ORM như một lớp repository để truy cập dữ liệu, tách biệt logic nghiệp vụ khỏi truy cập dữ liệu.

### Mẫu Service
Tách logic nghiệp vụ phức tạp vào các lớp service riêng biệt, giúp views chỉ tập trung vào xử lý HTTP.

### Mẫu Template
Sử dụng hệ thống template của Django với kế thừa template để tái sử dụng code và duy trì tính nhất quán.

### Mẫu Form
Sử dụng Django Forms và ModelForms để xác thực dữ liệu đầu vào và tạo giao diện người dùng.

### Mẫu Signal
Sử dụng Django Signals để xử lý các sự kiện như tạo hồ sơ người dùng khi đăng ký.

## Luồng dữ liệu
### Luồng xác thực
```
flowchart LR
    User[User] --> Login[Login Form]
    Login --> AuthView[Authentication View]
    AuthView --> Validate[Validate Credentials]
    Validate --> Session[Create Session]
    Session --> Redirect[Redirect to Dashboard]
```

### Luồng học tập
```
flowchart LR
    User[User] --> SelectSubject[Select Subject]
    SelectSubject --> ViewLessons[View Lessons]
    ViewLessons --> StudyContent[Study Content]
    StudyContent --> TakeQuiz[Take Quiz]
    TakeQuiz --> ViewResults[View Results]
    ViewResults --> TrackProgress[Track Progress]
```

### Luồng tạo nội dung
```
flowchart LR
    Admin[Admin/Creator] --> CreateSubject[Create Subject]
    CreateSubject --> AddTopics[Add Topics]
    AddTopics --> CreateLessons[Create Lessons]
    CreateLessons --> AddQuizzes[Add Quizzes]
    AddQuizzes --> PublishContent[Publish Content]
```

## Tương tác frontend
### HTMX + Alpine.js
Sử dụng HTMX để tải nội dung động mà không cần tải lại trang, kết hợp với Alpine.js để xử lý tương tác phía client.

```
flowchart LR
    User[User] --> Interact[Interact with UI]
    Interact --> HTMX[HTMX Request]
    HTMX --> Server[Server Process]
    Server --> Response[HTML Response]
    Response --> DOM[Update DOM]
    DOM --> Alpine[Alpine.js Reactivity]
```

## Bảo mật
### Các biện pháp bảo mật
1. **Xác thực**: Django's authentication system
2. **Phân quyền**: Django's permission system
3. **CSRF Protection**: Django's CSRF middleware
4. **XSS Protection**: Django's template escaping
5. **SQL Injection Protection**: Django ORM
6. **Secure Cookies**: SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE
7. **HTTPS**: SECURE_SSL_REDIRECT
8. **Content Security**: SECURE_CONTENT_TYPE_NOSNIFF, SECURE_BROWSER_XSS_FILTER

## Khả năng mở rộng
### Chiến lược mở rộng
1. **Database Optimization**: Indexing, query optimization
2. **Caching**: Django's cache framework
3. **Asynchronous Tasks**: Background processing
4. **Load Balancing**: Multiple server instances
5. **Content Delivery Network**: Static files distribution
6. **Database Sharding**: Data partitioning for large datasets
