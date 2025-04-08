import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

class NotificationConsumer(AsyncWebsocketConsumer):
    """Consumer xử lý kết nối WebSocket cho thông báo thời gian thực"""
    
    async def connect(self):
        """Xử lý khi client kết nối WebSocket"""
        # Kiểm tra xác thực người dùng
        if self.scope["user"].is_anonymous:
            # Từ chối kết nối nếu người dùng chưa đăng nhập
            await self.close()
            return
        
        # Lấy ID người dùng từ scope
        self.user_id = self.scope["user"].id
        
        # Tạo tên nhóm dựa trên ID người dùng
        self.notification_group_name = f"notifications_{self.user_id}"
        
        # Thêm kênh vào nhóm
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        # Chấp nhận kết nối
        await self.accept()
        
        # Gửi thông báo chưa đọc khi kết nối
        await self.send_unread_notifications()
    
    async def disconnect(self, close_code):
        """Xử lý khi client ngắt kết nối WebSocket"""
        # Xóa kênh khỏi nhóm
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Xử lý khi nhận dữ liệu từ client"""
        try:
            data = json.loads(text_data)
            action = data.get("action")
            
            if action == "mark_read":
                notification_id = data.get("notification_id")
                if notification_id:
                    # Đánh dấu thông báo đã đọc
                    success = await self.mark_notification_read(notification_id)
                    # Gửi phản hồi về client
                    await self.send(text_data=json.dumps({
                        "type": "notification_marked_read",
                        "notification_id": notification_id,
                        "success": success
                    }))
            
            elif action == "mark_all_read":
                # Đánh dấu tất cả thông báo đã đọc
                success = await self.mark_all_notifications_read()
                # Gửi phản hồi về client
                await self.send(text_data=json.dumps({
                    "type": "all_notifications_marked_read",
                    "success": success
                }))
        
        except json.JSONDecodeError:
            # Gửi thông báo lỗi nếu dữ liệu không phải JSON hợp lệ
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Invalid JSON format"
            }))
    
    async def notification_message(self, event):
        """Xử lý khi nhận thông báo từ channel layer"""
        # Gửi thông báo đến client
        await self.send(text_data=json.dumps({
            "type": "new_notification",
            "notification": event["notification"]
        }))
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Đánh dấu thông báo đã đọc"""
        from notifications.models import Notification
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user_id=self.user_id
            )
            notification.is_read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    @database_sync_to_async
    def mark_all_notifications_read(self):
        """Đánh dấu tất cả thông báo đã đọc"""
        from notifications.models import Notification
        try:
            Notification.objects.filter(
                user_id=self.user_id,
                is_read=False
            ).update(is_read=True)
            return True
        except Exception:
            return False
    
    @database_sync_to_async
    def get_unread_notifications(self):
        """Lấy danh sách thông báo chưa đọc"""
        from notifications.models import Notification
        notifications = Notification.objects.filter(
            user_id=self.user_id,
            is_read=False
        ).order_by('-created_at')[:10]
        
        return [
            {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.notification_type,
                "feature": notification.related_feature,
                "url": notification.url,
                "created_at": notification.created_at.isoformat(),
            }
            for notification in notifications
        ]
    
    async def send_unread_notifications(self):
        """Gửi danh sách thông báo chưa đọc khi kết nối"""
        unread_notifications = await self.get_unread_notifications()
        await self.send(text_data=json.dumps({
            "type": "unread_notifications",
            "notifications": unread_notifications
        }))
