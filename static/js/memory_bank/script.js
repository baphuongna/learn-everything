// Memory Bank JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Xử lý lật thẻ ôn tập
    const reviewCard = document.getElementById('review-card');
    if (reviewCard) {
        reviewCard.addEventListener('click', function() {
            this.classList.toggle('flipped');
        });
    }
    
    // Xử lý nút yêu thích
    const toggleFavoriteBtn = document.getElementById('toggle-favorite');
    if (toggleFavoriteBtn) {
        toggleFavoriteBtn.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item-id');
            
            // Lấy CSRF token từ cookie
            function getCookie(name) {
                let cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim();
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            const csrftoken = getCookie('csrftoken');
            
            // Gửi yêu cầu AJAX để chuyển đổi trạng thái yêu thích
            fetch(`/memory/items/${itemId}/toggle-favorite/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Cập nhật giao diện
                    if (data.is_favorite) {
                        toggleFavoriteBtn.classList.remove('btn-outline-warning');
                        toggleFavoriteBtn.classList.add('btn-warning');
                        toggleFavoriteBtn.innerHTML = '<i class="fas fa-star"></i> Đã yêu thích';
                    } else {
                        toggleFavoriteBtn.classList.remove('btn-warning');
                        toggleFavoriteBtn.classList.add('btn-outline-warning');
                        toggleFavoriteBtn.innerHTML = '<i class="fas fa-star"></i> Yêu thích';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
    
    // Hiển thị tên file khi chọn file
    const fileInput = document.getElementById('id_file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'Không có file nào được chọn';
            const fileLabel = document.querySelector('label[for="id_file"]');
            fileLabel.textContent = 'Tập tin đính kèm: ' + fileName;
        });
    }
    
    // Xử lý chọn màu cho danh mục
    const colorInput = document.getElementById('id_color');
    if (colorInput) {
        colorInput.addEventListener('change', function() {
            const iconPreview = document.getElementById('icon-preview');
            if (iconPreview) {
                iconPreview.style.color = this.value;
            }
        });
    }
    
    // Xử lý chọn icon cho danh mục
    const iconInput = document.getElementById('id_icon');
    if (iconInput) {
        iconInput.addEventListener('change', function() {
            const iconPreview = document.getElementById('icon-preview');
            if (iconPreview) {
                iconPreview.className = this.value;
            }
        });
    }
});
