from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum

from .models import Badge, UserBadge, RewardPoint, PointHistory, Reward, UserReward

@login_required
def achievement_dashboard(request):
    """Trang tổng quan thành tích"""
    # Lấy tham số từ request
    format_type = request.GET.get('format', '')
    section = request.GET.get('section', '')

    # Lấy thông tin điểm thưởng
    reward_point, _ = RewardPoint.objects.get_or_create(user=request.user)

    # Lấy các huy hiệu của người dùng
    user_badges = UserBadge.objects.filter(user=request.user).select_related('badge')

    # Lấy các phần thưởng của người dùng
    user_rewards = UserReward.objects.filter(user=request.user).select_related('reward')

    # Thống kê huy hiệu theo danh mục
    badge_stats = {}
    for category, category_name in Badge.BADGE_CATEGORIES:
        total_badges = Badge.objects.filter(category=category).count()
        earned_badges = user_badges.filter(badge__category=category).count()
        badge_stats[category] = {
            'name': category_name,
            'total': total_badges,
            'earned': earned_badges,
            'percentage': int(earned_badges / total_badges * 100) if total_badges > 0 else 0
        }

    # Huy hiệu mới nhận
    recent_badges = user_badges.order_by('-earned_at')[:5]

    # Phần thưởng mới đổi
    recent_rewards = user_rewards.order_by('-redeemed_at')[:5]

    # Lịch sử điểm thưởng
    point_history = PointHistory.objects.filter(user=request.user).order_by('-timestamp')[:10]

    context = {
        'reward_point': reward_point,
        'user_badges_count': user_badges.count(),
        'user_rewards_count': user_rewards.count(),
        'badge_stats': badge_stats,
        'recent_badges': recent_badges,
        'recent_rewards': recent_rewards,
        'point_history': point_history,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        if section == 'badges':
            return render(request, 'achievements/dashboard_badges_partial.html', context)
        elif section == 'rewards':
            return render(request, 'achievements/dashboard_rewards_partial.html', context)
        elif section == 'points':
            return render(request, 'achievements/dashboard_points_partial.html', context)
        else:
            return render(request, 'achievements/dashboard_partial.html', context)

    return render(request, 'achievements/dashboard.html', context)

@login_required
def badge_list(request):
    """Danh sách huy hiệu"""
    # Lọc theo danh mục
    category = request.GET.get('category', '')
    level = request.GET.get('level', '')
    format_type = request.GET.get('format', '')

    # Lấy tất cả huy hiệu
    badges = Badge.objects.all()

    # Áp dụng bộ lọc
    if category:
        badges = badges.filter(category=category)
    if level:
        badges = badges.filter(level=level)

    # Lấy các huy hiệu của người dùng
    user_badges = UserBadge.objects.filter(user=request.user).values_list('badge_id', flat=True)

    # Thêm trường đánh dấu huy hiệu đã nhận
    for badge in badges:
        badge.is_earned = badge.id in user_badges

    context = {
        'badges': badges,
        'categories': Badge.BADGE_CATEGORIES,
        'levels': Badge.BADGE_LEVELS,
        'selected_category': category,
        'selected_level': level,
        'earned_count': len(user_badges),
        'total_count': badges.count(),
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'achievements/badge_list_partial.html', context)

    return render(request, 'achievements/badge_list.html', context)

@login_required
def reward_list(request):
    """Danh sách phần thưởng"""
    # Lấy tham số từ request
    format_type = request.GET.get('format', '')
    section = request.GET.get('section', '')

    # Lấy điểm thưởng của người dùng
    reward_point, _ = RewardPoint.objects.get_or_create(user=request.user)

    # Lấy các phần thưởng có thể đổi
    available_rewards = Reward.objects.filter(is_active=True).order_by('points_required')

    # Lấy các phần thưởng của người dùng
    user_rewards = UserReward.objects.filter(user=request.user).select_related('reward')

    # Phần thưởng chưa sử dụng
    unused_rewards = user_rewards.filter(is_used=False)

    # Phần thưởng đã sử dụng
    used_rewards = user_rewards.filter(is_used=True)

    context = {
        'reward_point': reward_point,
        'available_rewards': available_rewards,
        'unused_rewards': unused_rewards,
        'used_rewards': used_rewards,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        if section == 'available':
            return render(request, 'achievements/reward_available_partial.html', context)
        elif section == 'unused':
            return render(request, 'achievements/reward_unused_partial.html', context)
        elif section == 'used':
            return render(request, 'achievements/reward_used_partial.html', context)
        else:
            return render(request, 'achievements/reward_list_partial.html', context)

    return render(request, 'achievements/reward_list.html', context)

@login_required
def redeem_reward(request, reward_id):
    """\u0110\u1ed5i ph\u1ea7n th\u01b0\u1edfng"""
    if request.method != 'POST':
        return redirect('achievements:reward_list')

    # Lấy phần thưởng
    reward = get_object_or_404(Reward, id=reward_id, is_active=True)

    # Lấy điểm thưởng của người dùng
    reward_point, _ = RewardPoint.objects.get_or_create(user=request.user)

    # Kiểm tra xem người dùng có đủ điểm không
    if reward_point.points < reward.points_required:
        if request.htmx:
            context = {
                'error': f'Bạn không đủ điểm để đổi phần thưởng này. Cần {reward.points_required} điểm.',
                'reward': reward
            }
            return render(request, 'achievements/redeem_error.html', context)

        messages.error(request, f'Bạn không đủ điểm để đổi phần thưởng này. Cần {reward.points_required} điểm.')
        return redirect('achievements:reward_list')

    try:
        # Trừ điểm thưởng
        reward_point.use_points(reward.points_required, f'Đổi phần thưởng {reward.name}')

        # Tạo phần thưởng cho người dùng
        user_reward = UserReward.objects.create(
            user=request.user,
            reward=reward
        )

        if request.htmx:
            # Lấy các phần thưởng của người dùng
            unused_rewards = UserReward.objects.filter(user=request.user, is_used=False).select_related('reward')

            context = {
                'success': f'Bạn đã đổi thành công phần thưởng {reward.name}!',
                'reward_point': reward_point,
                'user_reward': user_reward,
                'unused_rewards': unused_rewards
            }
            return render(request, 'achievements/redeem_success.html', context)

        messages.success(request, f'Bạn đã đổi thành công phần thưởng {reward.name}!')
    except Exception as e:
        if request.htmx:
            context = {
                'error': f'Có lỗi xảy ra: {str(e)}',
                'reward': reward
            }
            return render(request, 'achievements/redeem_error.html', context)

        messages.error(request, f'Có lỗi xảy ra: {str(e)}')

    return redirect('achievements:reward_list')

@login_required
def use_reward(request, user_reward_id):
    """Sử dụng phần thưởng"""
    if request.method != 'POST':
        return redirect('achievements:reward_list')

    # Lấy phần thưởng của người dùng
    user_reward = get_object_or_404(UserReward, id=user_reward_id, user=request.user, is_used=False)

    try:
        # Đánh dấu phần thưởng đã sử dụng
        user_reward.use_reward()

        if request.htmx:
            # Lấy các phần thưởng của người dùng
            used_rewards = UserReward.objects.filter(user=request.user, is_used=True).select_related('reward')

            context = {
                'success': f'Bạn đã sử dụng phần thưởng {user_reward.reward.name}!',
                'user_reward': user_reward,
                'used_rewards': used_rewards
            }
            return render(request, 'achievements/use_reward_success.html', context)

        messages.success(request, f'Bạn đã sử dụng phần thưởng {user_reward.reward.name}!')
    except Exception as e:
        if request.htmx:
            context = {
                'error': f'Có lỗi xảy ra: {str(e)}',
                'user_reward': user_reward
            }
            return render(request, 'achievements/use_reward_error.html', context)

        messages.error(request, f'Có lỗi xảy ra: {str(e)}')

    return redirect('achievements:reward_list')

@login_required
def point_history(request):
    """Lịch sử điểm thưởng"""
    # Lấy tham số từ request
    format_type = request.GET.get('format', '')

    # Lấy điểm thưởng của người dùng
    reward_point, _ = RewardPoint.objects.get_or_create(user=request.user)

    # Lọc theo loại hành động
    action_type = request.GET.get('type', '')

    # Lấy lịch sử điểm thưởng
    history = PointHistory.objects.filter(user=request.user)

    # Áp dụng bộ lọc
    if action_type:
        history = history.filter(action_type=action_type)

    # Tổng điểm nhận được
    total_earned = history.filter(action_type='earn').aggregate(total=Sum('points'))['total'] or 0

    # Tổng điểm đã sử dụng
    total_used = history.filter(action_type='use').aggregate(total=Sum('points'))['total'] or 0

    context = {
        'reward_point': reward_point,
        'history': history.order_by('-timestamp'),
        'total_earned': total_earned,
        'total_used': total_used,
        'selected_type': action_type,
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'achievements/point_history_partial.html', context)

    return render(request, 'achievements/point_history.html', context)