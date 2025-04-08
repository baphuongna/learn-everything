from django.contrib import admin
from .models import Badge, UserBadge, RewardPoint, PointHistory, Reward, UserReward

class UserBadgeInline(admin.TabularInline):
    model = UserBadge
    extra = 0
    readonly_fields = ['earned_at']

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'level', 'points', 'condition_type', 'condition_value']
    list_filter = ['category', 'level']
    search_fields = ['name', 'description']
    fieldsets = [
        ('Thông tin cơ bản', {
            'fields': ['name', 'description', 'category', 'level', 'icon', 'points']
        }),
        ('Điều kiện', {
            'fields': ['condition_type', 'condition_value']
        }),
    ]
    inlines = [UserBadgeInline]

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at']
    list_filter = ['badge__category', 'badge__level', 'earned_at']
    search_fields = ['user__username', 'badge__name']
    date_hierarchy = 'earned_at'

class PointHistoryInline(admin.TabularInline):
    model = PointHistory
    extra = 0
    readonly_fields = ['timestamp', 'action_type', 'points', 'reason']
    can_delete = False
    max_num = 10
    ordering = ['-timestamp']
    fk_name = 'user'

@admin.register(RewardPoint)
class RewardPointAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'lifetime_points']
    search_fields = ['user__username']
    readonly_fields = ['lifetime_points']

@admin.register(PointHistory)
class PointHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'points', 'reason', 'timestamp']
    list_filter = ['action_type', 'timestamp']
    search_fields = ['user__username', 'reason']
    date_hierarchy = 'timestamp'
    readonly_fields = ['user', 'action_type', 'points', 'reason', 'timestamp']

class UserRewardInline(admin.TabularInline):
    model = UserReward
    extra = 0
    readonly_fields = ['redeemed_at', 'is_used', 'used_at']

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['name', 'points_required', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    fieldsets = [
        ('Thông tin cơ bản', {
            'fields': ['name', 'description', 'points_required', 'icon', 'is_active']
        }),
    ]
    inlines = [UserRewardInline]

@admin.register(UserReward)
class UserRewardAdmin(admin.ModelAdmin):
    list_display = ['user', 'reward', 'redeemed_at', 'is_used', 'used_at']
    list_filter = ['is_used', 'redeemed_at']
    search_fields = ['user__username', 'reward__name']
    date_hierarchy = 'redeemed_at'