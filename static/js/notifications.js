/**
 * Quản lý thông báo thời gian thực qua WebSocket
 */
class NotificationManager {
    constructor() {
        this.socket = null;
        this.notificationCount = 0;
        this.notificationList = [];
        this.notificationContainer = document.getElementById('notification-dropdown');
        this.notificationBadge = document.getElementById('notification-badge');
        this.notificationToggle = document.getElementById('notification-toggle');
        this.notificationContent = document.getElementById('notification-content');
        this.markAllReadBtn = document.getElementById('mark-all-read-btn');
        
        this.init();
    }
    
    /**
     * Khởi tạo kết nối WebSocket và các sự kiện
     */
    init() {
        // Kiểm tra xem trình duyệt có hỗ trợ WebSocket không
        if (!('WebSocket' in window)) {
            console.error('Trình duyệt không hỗ trợ WebSocket');
            return;
        }
        
        // Tạo kết nối WebSocket
        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsUrl = `${protocol}${window.location.host}/ws/notifications/`;
        
        this.socket = new WebSocket(wsUrl);
        
        // Xử lý sự kiện khi kết nối mở
        this.socket.onopen = () => {
            console.log('Kết nối WebSocket đã được thiết lập');
        };
        
        // Xử lý sự kiện khi nhận dữ liệu
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleSocketMessage(data);
        };
        
        // Xử lý sự kiện khi kết nối đóng
        this.socket.onclose = (event) => {
            console.log('Kết nối WebSocket đã đóng', event);
            
            // Thử kết nối lại sau 5 giây
            setTimeout(() => {
                this.init();
            }, 5000);
        };
        
        // Xử lý sự kiện khi có lỗi
        this.socket.onerror = (error) => {
            console.error('Lỗi WebSocket:', error);
        };
        
        // Thêm sự kiện cho nút đánh dấu tất cả đã đọc
        if (this.markAllReadBtn) {
            this.markAllReadBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.markAllAsRead();
            });
        }
    }
    
    /**
     * Xử lý tin nhắn từ WebSocket
     * @param {Object} data - Dữ liệu nhận được từ WebSocket
     */
    handleSocketMessage(data) {
        switch (data.type) {
            case 'unread_notifications':
                // Nhận danh sách thông báo chưa đọc khi kết nối
                this.notificationList = data.notifications;
                this.notificationCount = this.notificationList.length;
                this.updateNotificationBadge();
                this.updateNotificationDropdown();
                break;
                
            case 'new_notification':
                // Nhận thông báo mới
                this.notificationList.unshift(data.notification);
                this.notificationCount++;
                this.updateNotificationBadge();
                this.updateNotificationDropdown();
                this.showToast(data.notification);
                break;
                
            case 'notification_marked_read':
                // Xử lý khi thông báo được đánh dấu đã đọc
                if (data.success) {
                    this.removeNotificationFromList(data.notification_id);
                    this.updateNotificationBadge();
                    this.updateNotificationDropdown();
                }
                break;
                
            case 'all_notifications_marked_read':
                // Xử lý khi tất cả thông báo được đánh dấu đã đọc
                if (data.success) {
                    this.notificationList = [];
                    this.notificationCount = 0;
                    this.updateNotificationBadge();
                    this.updateNotificationDropdown();
                }
                break;
        }
    }
    
    /**
     * Cập nhật badge hiển thị số lượng thông báo
     */
    updateNotificationBadge() {
        if (this.notificationBadge) {
            if (this.notificationCount > 0) {
                this.notificationBadge.textContent = this.notificationCount > 99 ? '99+' : this.notificationCount;
                this.notificationBadge.classList.remove('d-none');
            } else {
                this.notificationBadge.classList.add('d-none');
            }
        }
    }
    
    /**
     * Cập nhật nội dung dropdown thông báo
     */
    updateNotificationDropdown() {
        if (!this.notificationContent) return;
        
        if (this.notificationList.length === 0) {
            this.notificationContent.innerHTML = `
                <div class="text-center p-3">
                    <i class="fas fa-bell-slash text-muted mb-2" style="font-size: 2rem;"></i>
                    <p class="text-muted">Không có thông báo mới</p>
                </div>
            `;
            
            // Ẩn nút đánh dấu tất cả đã đọc
            if (this.markAllReadBtn) {
                this.markAllReadBtn.classList.add('d-none');
            }
            
            return;
        }
        
        // Hiển thị nút đánh dấu tất cả đã đọc
        if (this.markAllReadBtn) {
            this.markAllReadBtn.classList.remove('d-none');
        }
        
        // Tạo HTML cho danh sách thông báo
        let html = '';
        
        this.notificationList.forEach(notification => {
            let iconClass = 'fa-info-circle text-info';
            
            if (notification.type === 'success') {
                iconClass = 'fa-check-circle text-success';
            } else if (notification.type === 'warning') {
                iconClass = 'fa-exclamation-triangle text-warning';
            } else if (notification.type === 'danger') {
                iconClass = 'fa-exclamation-circle text-danger';
            }
            
            html += `
                <div class="dropdown-item notification-item" data-id="${notification.id}">
                    <div class="d-flex align-items-center">
                        <div class="notification-icon me-3">
                            <i class="fas ${iconClass}"></i>
                        </div>
                        <div class="notification-content">
                            <div class="notification-title">${notification.title}</div>
                            <div class="notification-text small">${notification.message}</div>
                            <div class="notification-time small text-muted">
                                ${this.formatDate(notification.created_at)}
                            </div>
                        </div>
                    </div>
                    <div class="notification-actions mt-2">
                        <div class="btn-group btn-group-sm w-100">
                            ${notification.url ? `<a href="${notification.url}" class="btn btn-outline-primary btn-sm">Xem</a>` : ''}
                            <button class="btn btn-outline-success btn-sm mark-read-btn" data-id="${notification.id}">Đã đọc</button>
                        </div>
                    </div>
                </div>
                <div class="dropdown-divider"></div>
            `;
        });
        
        // Thêm liên kết đến trang thông báo
        html += `
            <a class="dropdown-item text-center" href="/notifications/">
                <strong>Xem tất cả thông báo</strong>
            </a>
        `;
        
        this.notificationContent.innerHTML = html;
        
        // Thêm sự kiện cho các nút đánh dấu đã đọc
        const markReadBtns = this.notificationContent.querySelectorAll('.mark-read-btn');
        markReadBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const notificationId = btn.getAttribute('data-id');
                this.markAsRead(notificationId);
            });
        });
    }
    
    /**
     * Hiển thị toast thông báo
     * @param {Object} notification - Thông báo cần hiển thị
     */
    showToast(notification) {
        // Kiểm tra xem Bootstrap có được tải không
        if (typeof bootstrap === 'undefined' || !bootstrap.Toast) {
            console.error('Bootstrap Toast không khả dụng');
            return;
        }
        
        // Tạo element cho toast
        const toastEl = document.createElement('div');
        toastEl.className = 'toast';
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        // Xác định màu nền dựa trên loại thông báo
        let bgClass = 'bg-info';
        if (notification.type === 'success') {
            bgClass = 'bg-success';
        } else if (notification.type === 'warning') {
            bgClass = 'bg-warning';
        } else if (notification.type === 'danger') {
            bgClass = 'bg-danger';
        }
        
        // Tạo nội dung cho toast
        toastEl.innerHTML = `
            <div class="toast-header ${bgClass} text-white">
                <strong class="me-auto">${notification.title}</strong>
                <small>${this.formatDate(notification.created_at)}</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${notification.message}
                ${notification.url ? `<div class="mt-2"><a href="${notification.url}" class="btn btn-sm btn-primary">Xem chi tiết</a></div>` : ''}
            </div>
        `;
        
        // Thêm toast vào container
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            // Tạo container nếu chưa tồn tại
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
            container.appendChild(toastEl);
        } else {
            toastContainer.appendChild(toastEl);
        }
        
        // Hiển thị toast
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 5000
        });
        toast.show();
        
        // Xóa toast khỏi DOM sau khi ẩn
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }
    
    /**
     * Đánh dấu thông báo đã đọc
     * @param {number} notificationId - ID của thông báo
     */
    markAsRead(notificationId) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                action: 'mark_read',
                notification_id: notificationId
            }));
        }
    }
    
    /**
     * Đánh dấu tất cả thông báo đã đọc
     */
    markAllAsRead() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                action: 'mark_all_read'
            }));
        }
    }
    
    /**
     * Xóa thông báo khỏi danh sách
     * @param {number} notificationId - ID của thông báo
     */
    removeNotificationFromList(notificationId) {
        const index = this.notificationList.findIndex(n => n.id === notificationId);
        if (index !== -1) {
            this.notificationList.splice(index, 1);
            this.notificationCount = this.notificationList.length;
        }
    }
    
    /**
     * Định dạng ngày giờ
     * @param {string} dateString - Chuỗi ngày giờ ISO
     * @returns {string} - Chuỗi ngày giờ đã định dạng
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHour = Math.floor(diffMin / 60);
        const diffDay = Math.floor(diffHour / 24);
        
        if (diffSec < 60) {
            return 'Vừa xong';
        } else if (diffMin < 60) {
            return `${diffMin} phút trước`;
        } else if (diffHour < 24) {
            return `${diffHour} giờ trước`;
        } else if (diffDay < 7) {
            return `${diffDay} ngày trước`;
        } else {
            return date.toLocaleDateString('vi-VN');
        }
    }
}

// Khởi tạo quản lý thông báo khi trang đã tải xong
document.addEventListener('DOMContentLoaded', () => {
    // Chỉ khởi tạo nếu người dùng đã đăng nhập (kiểm tra qua sự tồn tại của dropdown thông báo)
    if (document.getElementById('notification-dropdown')) {
        window.notificationManager = new NotificationManager();
    }
});
