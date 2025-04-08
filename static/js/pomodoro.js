/**
 * Pomodoro Timer JavaScript
 * Quản lý tính năng Pomodoro Timer
 */

class PomodoroTimer {
    /**
     * Khởi tạo Pomodoro Timer
     */
    constructor() {
        // Các phần tử DOM
        this.timerDisplay = document.getElementById('timer-display');
        this.timerPhase = document.getElementById('timer-phase');
        this.timerCard = document.getElementById('timer-card');
        this.timerProgress = document.getElementById('timer-progress');
        this.startBtn = document.getElementById('start-timer');
        this.pauseBtn = document.getElementById('pause-timer');
        this.resumeBtn = document.getElementById('resume-timer');
        this.resetBtn = document.getElementById('reset-timer');
        this.skipBtn = document.getElementById('skip-timer');
        this.pomodoroCount = document.getElementById('pomodoro-count');
        this.pomodoroIcons = document.getElementById('pomodoro-icons');
        this.themeSwitch = document.getElementById('theme-switch');
        
        // Biến trạng thái
        this.isRunning = false;
        this.isPaused = false;
        this.isWorkPhase = true;
        this.timerInterval = null;
        this.sessionId = null;
        this.completedPomodoros = 0;
        this.totalSeconds = 0;
        this.currentSeconds = 0;
        this.workDuration = parseInt(document.getElementById('work_duration').value) * 60;
        this.breakDuration = parseInt(document.getElementById('break_duration').value) * 60;
        this.longBreakDuration = parseInt(document.getElementById('long_break_duration')?.value || 15) * 60;
        this.pomodorosUntilLongBreak = parseInt(document.getElementById('pomodoros_until_long_break')?.value || 4);
        
        // Âm thanh thông báo
        this.alarmSound = new Audio('/static/sounds/alarm.mp3');
        this.tickSound = new Audio('/static/sounds/tick.mp3');
        this.enableSounds = document.getElementById('enable_sounds')?.checked || true;
        
        // Thông báo trình duyệt
        this.enableNotifications = document.getElementById('enable_notifications')?.checked || false;
        this.notificationPermission = 'default';
        
        // Khởi tạo
        this.init();
    }
    
    /**
     * Khởi tạo timer và các sự kiện
     */
    init() {
        // Kiểm tra quyền thông báo
        if ('Notification' in window) {
            this.notificationPermission = Notification.permission;
            
            if (this.notificationPermission === 'default' && this.enableNotifications) {
                this.requestNotificationPermission();
            }
        }
        
        // Thêm sự kiện cho các nút
        if (this.startBtn) {
            this.startBtn.addEventListener('click', () => this.startTimer());
        }
        
        if (this.pauseBtn) {
            this.pauseBtn.addEventListener('click', () => this.pauseTimer());
        }
        
        if (this.resumeBtn) {
            this.resumeBtn.addEventListener('click', () => this.resumeTimer());
        }
        
        if (this.resetBtn) {
            this.resetBtn.addEventListener('click', () => this.resetTimer());
        }
        
        if (this.skipBtn) {
            this.skipBtn.addEventListener('click', () => this.skipPhase());
        }
        
        // Thêm sự kiện cho chuyển đổi theme
        if (this.themeSwitch) {
            this.themeSwitch.addEventListener('change', () => this.toggleTheme());
            
            // Thiết lập trạng thái ban đầu dựa trên theme hiện tại
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            this.themeSwitch.checked = currentTheme === 'dark';
        }
        
        // Thêm sự kiện cho các tùy chọn
        const enableSoundsCheckbox = document.getElementById('enable_sounds');
        if (enableSoundsCheckbox) {
            enableSoundsCheckbox.addEventListener('change', (e) => {
                this.enableSounds = e.target.checked;
            });
        }
        
        const enableNotificationsCheckbox = document.getElementById('enable_notifications');
        if (enableNotificationsCheckbox) {
            enableNotificationsCheckbox.addEventListener('change', (e) => {
                this.enableNotifications = e.target.checked;
                
                if (this.enableNotifications && this.notificationPermission === 'default') {
                    this.requestNotificationPermission();
                }
            });
        }
        
        // Xử lý sự kiện khi thay đổi chủ đề
        const subjectSelect = document.getElementById('subject');
        if (subjectSelect) {
            subjectSelect.addEventListener('change', () => this.loadTopics());
        }
        
        // Khởi tạo biểu đồ thống kê nếu có
        this.initCharts();
        
        // Cập nhật hiển thị timer
        this.updateTimerDisplay();
    }
    
    /**
     * Cập nhật hiển thị timer
     */
    updateTimerDisplay() {
        if (!this.timerDisplay) return;
        
        const minutes = Math.floor(this.currentSeconds / 60);
        const seconds = this.currentSeconds % 60;
        
        this.timerDisplay.textContent = 
            (minutes < 10 ? '0' + minutes : minutes) + ':' +
            (seconds < 10 ? '0' + seconds : seconds);
        
        // Cập nhật thanh tiến trình
        if (this.timerProgress && this.totalSeconds > 0) {
            const progressPercent = ((this.totalSeconds - this.currentSeconds) / this.totalSeconds) * 100;
            this.timerProgress.style.width = progressPercent + '%';
            
            // Thêm hiệu ứng pulse khi còn ít thời gian
            if (this.currentSeconds <= 60 && this.isRunning && !this.isPaused) {
                this.timerDisplay.classList.add('pulse-animation');
            } else {
                this.timerDisplay.classList.remove('pulse-animation');
            }
        }
        
        // Cập nhật tiêu đề trang
        document.title = `${this.timerDisplay.textContent} - ${this.isWorkPhase ? 'Làm việc' : 'Nghỉ'} - Pomodoro Timer`;
    }
    
    /**
     * Bắt đầu timer
     */
    startTimer() {
        // Lấy giá trị từ form
        this.workDuration = parseInt(document.getElementById('work_duration').value) * 60;
        this.breakDuration = parseInt(document.getElementById('break_duration').value) * 60;
        this.longBreakDuration = parseInt(document.getElementById('long_break_duration')?.value || 15) * 60;
        this.pomodorosUntilLongBreak = parseInt(document.getElementById('pomodoros_until_long_break')?.value || 4);
        
        // Thiết lập timer
        this.isWorkPhase = true;
        this.totalSeconds = this.workDuration;
        this.currentSeconds = this.workDuration;
        
        // Cập nhật giao diện
        this.timerPhase.textContent = 'Thời gian làm việc';
        this.timerCard.classList.remove('break');
        this.timerCard.classList.add('work');
        this.timerProgress.classList.remove('bg-success');
        this.timerProgress.classList.add('bg-danger');
        
        this.updateTimerDisplay();
        
        // Bắt đầu đếm ngược
        this.isRunning = true;
        this.isPaused = false;
        
        // Cập nhật nút
        this.startBtn.classList.add('d-none');
        this.pauseBtn.classList.remove('d-none');
        this.resumeBtn.classList.add('d-none');
        
        // Bắt đầu phiên Pomodoro mới
        this.startPomodoroSession();
        
        // Bắt đầu đếm ngược
        this.timerInterval = setInterval(() => this.tick(), 1000);
    }
    
    /**
     * Xử lý mỗi giây của timer
     */
    tick() {
        if (this.currentSeconds > 0) {
            this.currentSeconds--;
            
            // Phát âm thanh tick nếu được bật
            if (this.enableSounds && this.currentSeconds <= 10 && this.currentSeconds > 0) {
                this.tickSound.play();
            }
            
            this.updateTimerDisplay();
        } else {
            // Hết thời gian
            clearInterval(this.timerInterval);
            
            // Phát âm thanh báo nếu được bật
            if (this.enableSounds) {
                this.alarmSound.play();
            }
            
            // Hiển thị thông báo
            this.showNotification();
            
            if (this.isWorkPhase) {
                // Tăng số pomodoro đã hoàn thành
                this.completedPomodoros++;
                this.pomodoroCount.textContent = this.completedPomodoros;
                this.updatePomodoroIcons();
                
                // Kiểm tra xem có nên nghỉ dài không
                const isLongBreak = this.completedPomodoros % this.pomodorosUntilLongBreak === 0;
                
                // Chuyển sang thời gian nghỉ
                this.isWorkPhase = false;
                this.totalSeconds = isLongBreak ? this.longBreakDuration : this.breakDuration;
                this.currentSeconds = isLongBreak ? this.longBreakDuration : this.breakDuration;
                this.timerPhase.textContent = isLongBreak ? 'Thời gian nghỉ dài' : 'Thời gian nghỉ';
                this.timerCard.classList.remove('work');
                this.timerCard.classList.add('break');
                this.timerProgress.classList.remove('bg-danger');
                this.timerProgress.classList.add('bg-success');
                
                // Tạo thông báo trong ứng dụng
                this.createAppNotification('Pomodoro hoàn thành!', 
                    `Bạn đã hoàn thành ${this.completedPomodoros} pomodoro. Hãy nghỉ ngơi ${isLongBreak ? this.longBreakDuration/60 : this.breakDuration/60} phút.`);
            } else {
                // Chuyển lại thời gian làm việc
                this.isWorkPhase = true;
                this.totalSeconds = this.workDuration;
                this.currentSeconds = this.workDuration;
                this.timerPhase.textContent = 'Thời gian làm việc';
                this.timerCard.classList.remove('break');
                this.timerCard.classList.add('work');
                this.timerProgress.classList.remove('bg-success');
                this.timerProgress.classList.add('bg-danger');
                
                // Tạo thông báo trong ứng dụng
                this.createAppNotification('Thời gian nghỉ kết thúc!', 
                    'Hãy quay lại làm việc. Bạn có thể làm được!');
            }
            
            this.updateTimerDisplay();
            
            // Tự động bắt đầu lại timer
            this.timerInterval = setInterval(() => this.tick(), 1000);
        }
    }
    
    /**
     * Tạm dừng timer
     */
    pauseTimer() {
        if (this.isRunning && !this.isPaused) {
            clearInterval(this.timerInterval);
            this.isPaused = true;
            this.pauseBtn.classList.add('d-none');
            this.resumeBtn.classList.remove('d-none');
            
            // Cập nhật tiêu đề trang
            document.title = `${this.timerDisplay.textContent} - Tạm dừng - Pomodoro Timer`;
        }
    }
    
    /**
     * Tiếp tục timer
     */
    resumeTimer() {
        if (this.isRunning && this.isPaused) {
            this.isPaused = false;
            this.pauseBtn.classList.remove('d-none');
            this.resumeBtn.classList.add('d-none');
            
            this.timerInterval = setInterval(() => this.tick(), 1000);
        }
    }
    
    /**
     * Đặt lại timer
     */
    resetTimer() {
        clearInterval(this.timerInterval);
        this.isRunning = false;
        this.isPaused = false;
        
        // Đặt lại thời gian
        this.isWorkPhase = true;
        this.workDuration = parseInt(document.getElementById('work_duration').value) * 60;
        this.breakDuration = parseInt(document.getElementById('break_duration').value) * 60;
        this.totalSeconds = this.workDuration;
        this.currentSeconds = this.workDuration;
        
        // Cập nhật giao diện
        this.timerPhase.textContent = 'Sẵn sàng bắt đầu';
        this.timerCard.classList.remove('break');
        this.timerCard.classList.add('work');
        this.timerProgress.style.width = '0%';
        this.timerProgress.classList.remove('bg-success');
        this.timerProgress.classList.add('bg-danger');
        
        // Cập nhật nút
        this.startBtn.classList.remove('d-none');
        this.pauseBtn.classList.add('d-none');
        this.resumeBtn.classList.add('d-none');
        
        this.updateTimerDisplay();
        
        // Kết thúc phiên hiện tại nếu có
        if (this.sessionId) {
            this.endPomodoroSession();
        }
        
        // Cập nhật tiêu đề trang
        document.title = 'Pomodoro Timer - Nền Tảng Học Tập';
    }
    
    /**
     * Bỏ qua giai đoạn hiện tại
     */
    skipPhase() {
        clearInterval(this.timerInterval);
        
        if (this.isWorkPhase) {
            // Chuyển sang thời gian nghỉ
            this.isWorkPhase = false;
            this.totalSeconds = this.breakDuration;
            this.currentSeconds = this.breakDuration;
            this.timerPhase.textContent = 'Thời gian nghỉ';
            this.timerCard.classList.remove('work');
            this.timerCard.classList.add('break');
            this.timerProgress.classList.remove('bg-danger');
            this.timerProgress.classList.add('bg-success');
            
            // Tăng số pomodoro đã hoàn thành
            this.completedPomodoros++;
            this.pomodoroCount.textContent = this.completedPomodoros;
            this.updatePomodoroIcons();
        } else {
            // Chuyển lại thời gian làm việc
            this.isWorkPhase = true;
            this.totalSeconds = this.workDuration;
            this.currentSeconds = this.workDuration;
            this.timerPhase.textContent = 'Thời gian làm việc';
            this.timerCard.classList.remove('break');
            this.timerCard.classList.add('work');
            this.timerProgress.classList.remove('bg-success');
            this.timerProgress.classList.add('bg-danger');
        }
        
        this.updateTimerDisplay();
        
        // Tiếp tục timer
        if (this.isRunning && !this.isPaused) {
            this.timerInterval = setInterval(() => this.tick(), 1000);
        }
    }
    
    /**
     * Cập nhật biểu tượng pomodoro
     */
    updatePomodoroIcons() {
        if (!this.pomodoroIcons) return;
        
        this.pomodoroIcons.innerHTML = '';
        for (let i = 0; i < this.completedPomodoros; i++) {
            const icon = document.createElement('i');
            icon.className = 'fas fa-apple-alt tomato';
            icon.setAttribute('data-bs-toggle', 'tooltip');
            icon.setAttribute('data-bs-placement', 'top');
            icon.setAttribute('title', `Pomodoro #${i+1}`);
            this.pomodoroIcons.appendChild(icon);
        }
        
        // Khởi tạo tooltips
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }
    
    /**
     * Bắt đầu phiên Pomodoro mới
     */
    startPomodoroSession() {
        // Lấy dữ liệu từ form
        const formData = new FormData(document.getElementById('pomodoro-settings-form'));
        
        // Gửi yêu cầu AJAX để bắt đầu phiên mới
        fetch('/advanced_learning/pomodoro/start/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.sessionId = data.session_id;
                console.log('Phiên Pomodoro mới đã bắt đầu:', data);
            }
        })
        .catch(error => {
            console.error('Lỗi khi bắt đầu phiên Pomodoro:', error);
        });
    }
    
    /**
     * Kết thúc phiên Pomodoro
     */
    endPomodoroSession() {
        if (!this.sessionId) return;
        
        // Tạo FormData
        const formData = new FormData();
        formData.append('session_id', this.sessionId);
        formData.append('completed_pomodoros', this.completedPomodoros);
        
        // Thêm CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Gửi yêu cầu AJAX để kết thúc phiên
        fetch('/advanced_learning/pomodoro/end/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Phiên Pomodoro đã kết thúc:', data);
                this.sessionId = null;
                this.completedPomodoros = 0;
                this.pomodoroCount.textContent = '0';
                this.pomodoroIcons.innerHTML = '';
            }
        })
        .catch(error => {
            console.error('Lỗi khi kết thúc phiên Pomodoro:', error);
        });
    }
    
    /**
     * Tải danh sách chủ đề con khi chọn chủ đề
     */
    loadTopics() {
        const subjectId = document.getElementById('subject').value;
        const topicSelect = document.getElementById('topic');
        
        if (!topicSelect) return;
        
        if (subjectId) {
            // Kích hoạt select topic
            topicSelect.disabled = false;
            
            // Gửi yêu cầu AJAX để lấy danh sách topic
            fetch(`/api/subjects/${subjectId}/topics/`)
                .then(response => response.json())
                .then(data => {
                    // Xóa các option cũ
                    topicSelect.innerHTML = '<option value="">-- Chọn chủ đề con --</option>';
                    
                    // Thêm các option mới
                    data.forEach(topic => {
                        const option = document.createElement('option');
                        option.value = topic.id;
                        option.textContent = topic.name;
                        topicSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Lỗi khi lấy danh sách chủ đề con:', error);
                });
        } else {
            // Vô hiệu hóa select topic
            topicSelect.disabled = true;
            topicSelect.innerHTML = '<option value="">-- Chọn chủ đề trước --</option>';
        }
    }
    
    /**
     * Chuyển đổi giữa light mode và dark mode
     */
    toggleTheme() {
        const isDarkMode = this.themeSwitch.checked;
        document.documentElement.setAttribute('data-bs-theme', isDarkMode ? 'dark' : 'light');
        
        // Lưu trạng thái vào localStorage
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    }
    
    /**
     * Yêu cầu quyền thông báo
     */
    requestNotificationPermission() {
        if (!('Notification' in window)) {
            console.log('Trình duyệt không hỗ trợ thông báo');
            return;
        }
        
        Notification.requestPermission().then(permission => {
            this.notificationPermission = permission;
            console.log('Quyền thông báo:', permission);
        });
    }
    
    /**
     * Hiển thị thông báo trên trình duyệt
     */
    showNotification() {
        // Kiểm tra xem thông báo có được bật không
        if (!this.enableNotifications) return;
        
        // Kiểm tra quyền thông báo
        if (!('Notification' in window) || this.notificationPermission !== 'granted') {
            return;
        }
        
        let title, body, icon;
        
        if (this.isWorkPhase) {
            // Kết thúc thời gian làm việc
            title = 'Thời gian làm việc kết thúc!';
            body = `Bạn đã hoàn thành ${this.completedPomodoros + 1} pomodoro. Hãy nghỉ ngơi một chút.`;
            icon = '/static/images/tomato.png';
        } else {
            // Kết thúc thời gian nghỉ
            title = 'Thời gian nghỉ kết thúc!';
            body = 'Hãy quay lại làm việc. Bạn có thể làm được!';
            icon = '/static/images/work.png';
        }
        
        // Hiển thị thông báo
        const notification = new Notification(title, {
            body: body,
            icon: icon
        });
        
        // Tự động đóng thông báo sau 5 giây
        setTimeout(() => {
            notification.close();
        }, 5000);
    }
    
    /**
     * Tạo thông báo trong ứng dụng
     */
    createAppNotification(title, message) {
        // Kiểm tra xem có NotificationManager không
        if (typeof window.notificationManager === 'undefined') {
            return;
        }
        
        // Tạo thông báo mới
        const notification = {
            title: title,
            message: message,
            type: this.isWorkPhase ? 'success' : 'info',
            related_feature: 'pomodoro'
        };
        
        // Hiển thị thông báo
        if (window.notificationManager.showToast) {
            window.notificationManager.showToast(notification);
        }
    }
    
    /**
     * Khởi tạo biểu đồ thống kê
     */
    initCharts() {
        // Kiểm tra xem có Chart.js không
        if (typeof Chart === 'undefined') {
            return;
        }
        
        // Biểu đồ thời gian học tập theo ngày
        const dailyChartCanvas = document.getElementById('daily-chart');
        if (dailyChartCanvas) {
            // Lấy dữ liệu từ thuộc tính data
            const chartData = JSON.parse(dailyChartCanvas.getAttribute('data-chart'));
            
            new Chart(dailyChartCanvas, {
                type: 'bar',
                data: {
                    labels: chartData.labels,
                    datasets: [{
                        label: 'Thời gian học tập (phút)',
                        data: chartData.data,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Biểu đồ phân bố thời gian học tập theo chủ đề
        const subjectChartCanvas = document.getElementById('subject-chart');
        if (subjectChartCanvas) {
            // Lấy dữ liệu từ thuộc tính data
            const chartData = JSON.parse(subjectChartCanvas.getAttribute('data-chart'));
            
            new Chart(subjectChartCanvas, {
                type: 'doughnut',
                data: {
                    labels: chartData.labels,
                    datasets: [{
                        data: chartData.data,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.2)',
                            'rgba(54, 162, 235, 0.2)',
                            'rgba(255, 206, 86, 0.2)',
                            'rgba(75, 192, 192, 0.2)',
                            'rgba(153, 102, 255, 0.2)',
                            'rgba(255, 159, 64, 0.2)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
    }
}

// Khởi tạo Pomodoro Timer khi trang đã tải xong
document.addEventListener('DOMContentLoaded', () => {
    // Thiết lập theme từ localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
        
        // Cập nhật trạng thái switch
        const themeSwitch = document.getElementById('theme-switch');
        if (themeSwitch) {
            themeSwitch.checked = savedTheme === 'dark';
        }
    }
    
    // Khởi tạo Pomodoro Timer
    window.pomodoroTimer = new PomodoroTimer();
});
