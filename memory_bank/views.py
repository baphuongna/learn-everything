from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import timedelta
import json

from .models import MemoryCategory, MemoryItem, MemoryAttachment
from .forms import MemoryCategoryForm, MemoryItemForm, MemoryAttachmentForm, MemorySearchForm

@login_required
def memory_home(request):
    """Trang chủ của Memory Bank"""
    format_type = request.GET.get('format', '')
    section = request.GET.get('section', '')

    # Lấy các danh mục của người dùng
    categories = MemoryCategory.objects.filter(user=request.user)

    # Lấy các ghi nhớ gần đây
    recent_items = MemoryItem.objects.filter(user=request.user).order_by('-updated_at')[:5]

    # Lấy các ghi nhớ yêu thích
    favorite_items = MemoryItem.objects.filter(user=request.user, is_favorite=True).order_by('-updated_at')[:5]

    # Lấy các ghi nhớ cần ôn tập hôm nay
    today = timezone.now()
    review_items = MemoryItem.objects.filter(
        user=request.user,
        next_review_date__lte=today
    ).order_by('next_review_date')[:5]

    # Tổng số ghi nhớ
    total_items = MemoryItem.objects.filter(user=request.user).count()
    total_review_items = MemoryItem.objects.filter(user=request.user, next_review_date__lte=today).count()

    context = {
        'categories': categories,
        'recent_items': recent_items,
        'favorite_items': favorite_items,
        'review_items': review_items,
        'total_items': total_items,
        'total_categories': categories.count(),
        'total_review_items': total_review_items
    }

    # Kiểm tra nếu là request HTMX partial cho một phần cụ thể
    if request.htmx and section:
        if section == 'recent':
            return render(request, 'memory_bank/partials/recent_items.html', context)
        elif section == 'favorite':
            return render(request, 'memory_bank/partials/favorite_items.html', context)
        elif section == 'review':
            return render(request, 'memory_bank/partials/review_items.html', context)
        elif section == 'stats':
            return render(request, 'memory_bank/partials/stats.html', context)

    # Kiểm tra nếu là request HTMX partial cho toàn bộ trang
    if format_type == 'partial' or request.htmx:
        return render(request, 'memory_bank/home_partial.html', context)

    return render(request, 'memory_bank/home.html', context)

@login_required
def memory_category_list(request):
    """Danh sách các danh mục ghi nhớ"""
    categories = MemoryCategory.objects.filter(user=request.user)

    if request.method == 'POST':
        form = MemoryCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Danh mục đã được tạo thành công!')
            return redirect('memory_category_list')
    else:
        form = MemoryCategoryForm()

    context = {
        'categories': categories,
        'form': form
    }

    return render(request, 'memory_bank/category_list.html', context)

@login_required
def memory_category_detail(request, slug):
    """Chi tiết danh mục và các ghi nhớ trong danh mục"""
    category = get_object_or_404(MemoryCategory, slug=slug, user=request.user)

    # Xử lý tìm kiếm và lọc
    search_form = MemorySearchForm(request.user, request.GET)
    items = MemoryItem.objects.filter(user=request.user, category=category)

    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        priority = search_form.cleaned_data.get('priority')
        is_favorite = search_form.cleaned_data.get('is_favorite')

        if query:
            items = items.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__icontains=query)
            )

        if priority:
            items = items.filter(priority=priority)

        if is_favorite:
            items = items.filter(is_favorite=True)

    # Phân trang
    paginator = Paginator(items, 10)  # 10 items mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Xử lý chỉnh sửa danh mục
    if request.method == 'POST':
        form = MemoryCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Danh mục đã được cập nhật thành công!')
            return redirect('memory_category_detail', slug=category.slug)
    else:
        form = MemoryCategoryForm(instance=category)

    context = {
        'category': category,
        'items': page_obj,
        'form': form,
        'search_form': search_form
    }

    return render(request, 'memory_bank/category_detail.html', context)

@login_required
def memory_category_delete(request, slug):
    """Xóa danh mục ghi nhớ"""
    category = get_object_or_404(MemoryCategory, slug=slug, user=request.user)

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Danh mục đã được xóa thành công!')
        return redirect('memory_category_list')

    return render(request, 'memory_bank/category_confirm_delete.html', {'category': category})

@login_required
def memory_item_create(request, category_slug=None):
    """Tạo ghi nhớ mới"""
    initial = {}
    if category_slug:
        category = get_object_or_404(MemoryCategory, slug=category_slug, user=request.user)
        initial['category'] = category

    if request.method == 'POST':
        form = MemoryItemForm(request.POST)
        attachment_form = MemoryAttachmentForm(request.POST, request.FILES)

        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user

            # Thiết lập ngày ôn tập tiếp theo (mặc định là ngày mai)
            item.next_review_date = timezone.now() + timedelta(days=1)
            item.save()

            # Xử lý tập tin đính kèm nếu có
            if attachment_form.is_valid() and 'file' in request.FILES:
                attachment = attachment_form.save(commit=False)
                attachment.memory_item = item
                attachment.save()

            messages.success(request, 'Ghi nhớ đã được tạo thành công!')
            return redirect('memory_item_detail', pk=item.pk)
    else:
        form = MemoryItemForm(initial=initial)
        attachment_form = MemoryAttachmentForm()

    # Chỉ hiển thị các danh mục của người dùng
    form.fields['category'].queryset = MemoryCategory.objects.filter(user=request.user)

    context = {
        'form': form,
        'attachment_form': attachment_form,
        'category_slug': category_slug
    }

    return render(request, 'memory_bank/item_form.html', context)

@login_required
def memory_item_detail(request, pk):
    """Chi tiết ghi nhớ"""
    item = get_object_or_404(MemoryItem, pk=pk, user=request.user)
    attachments = item.attachments.all()

    context = {
        'item': item,
        'attachments': attachments,
        'tags': item.get_tags_list()
    }

    return render(request, 'memory_bank/item_detail.html', context)

@login_required
def memory_item_edit(request, pk):
    """Chỉnh sửa ghi nhớ"""
    item = get_object_or_404(MemoryItem, pk=pk, user=request.user)

    if request.method == 'POST':
        form = MemoryItemForm(request.POST, instance=item)
        attachment_form = MemoryAttachmentForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            # Xử lý tập tin đính kèm nếu có
            if attachment_form.is_valid() and 'file' in request.FILES:
                attachment = attachment_form.save(commit=False)
                attachment.memory_item = item
                attachment.save()

            messages.success(request, 'Ghi nhớ đã được cập nhật thành công!')
            return redirect('memory_item_detail', pk=item.pk)
    else:
        form = MemoryItemForm(instance=item)
        attachment_form = MemoryAttachmentForm()

    # Chỉ hiển thị các danh mục của người dùng
    form.fields['category'].queryset = MemoryCategory.objects.filter(user=request.user)

    context = {
        'form': form,
        'attachment_form': attachment_form,
        'item': item,
        'attachments': item.attachments.all()
    }

    return render(request, 'memory_bank/item_form.html', context)

@login_required
def memory_item_delete(request, pk):
    """Xóa ghi nhớ"""
    item = get_object_or_404(MemoryItem, pk=pk, user=request.user)

    if request.method == 'POST':
        category = item.category
        item.delete()
        messages.success(request, 'Ghi nhớ đã được xóa thành công!')
        return redirect('memory_category_detail', slug=category.slug)

    return render(request, 'memory_bank/item_confirm_delete.html', {'item': item})

@login_required
def memory_attachment_delete(request, pk):
    """Xóa tập tin đính kèm"""
    attachment = get_object_or_404(MemoryAttachment, pk=pk, memory_item__user=request.user)

    if request.method == 'POST':
        item = attachment.memory_item
        attachment.delete()
        messages.success(request, 'Tập tin đính kèm đã được xóa thành công!')
        return redirect('memory_item_detail', pk=item.pk)

    return render(request, 'memory_bank/attachment_confirm_delete.html', {'attachment': attachment})

@login_required
def memory_item_toggle_favorite(request, pk):
    """Chuyển đổi trạng thái yêu thích của ghi nhớ"""
    if request.method == 'POST':
        item = get_object_or_404(MemoryItem, pk=pk, user=request.user)
        item.is_favorite = not item.is_favorite
        item.save()

        # Kiểm tra nếu là request HTMX
        if request.htmx:
            context = {
                'item': item,
                'message': 'Đã đánh dấu yêu thích' if item.is_favorite else 'Đã bỏ đánh dấu yêu thích'
            }
            return render(request, 'memory_bank/favorite_toggle_response.html', context)

        return JsonResponse({
            'success': True,
            'is_favorite': item.is_favorite
        })

    return JsonResponse({'success': False}, status=400)

@login_required
def memory_item_review(request, pk):
    """Xem lại và cập nhật lịch ôn tập của ghi nhớ"""
    item = get_object_or_404(MemoryItem, pk=pk, user=request.user)
    format_type = request.GET.get('format', '')

    if request.method == 'POST':
        recall_level = int(request.POST.get('recall_level', 1))

        # Cập nhật thông tin ôn tập
        item.last_review_date = timezone.now()
        item.review_count += 1

        # Tính ngày ôn tập tiếp theo dựa trên mức độ nhớ
        if recall_level == 1:  # Khó nhớ
            item.next_review_date = timezone.now() + timedelta(days=1)
        elif recall_level == 2:  # Nhớ mờ mờ
            item.next_review_date = timezone.now() + timedelta(days=3)
        else:  # Nhớ rõ
            item.next_review_date = timezone.now() + timedelta(days=7)

        item.save()

        # Đếm số ghi nhớ còn lại cần ôn tập
        today = timezone.now()
        remaining_count = MemoryItem.objects.filter(
            user=request.user,
            next_review_date__lte=today
        ).count()

        # Kiểm tra nếu là request HTMX
        if request.htmx:
            context = {
                'item': item,
                'recall_level': recall_level,
                'next_review_date': item.next_review_date,
                'remaining_count': remaining_count
            }
            return render(request, 'memory_bank/review_feedback.html', context)

        messages.success(request, 'Ghi nhớ đã được ôn tập thành công!')
        return redirect('memory_item_detail', pk=item.pk)

    context = {
        'item': item,
        'tags': item.get_tags_list(),
        'attachments': item.attachments.all()
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'memory_bank/item_review_partial.html', context)

    return render(request, 'memory_bank/item_review.html', context)

@login_required
def memory_review_list(request):
    """Danh sách các ghi nhớ cần ôn tập"""
    today = timezone.now()
    format_type = request.GET.get('format', '')

    items = MemoryItem.objects.filter(
        user=request.user,
        next_review_date__lte=today
    ).order_by('next_review_date')

    # Phân trang
    paginator = Paginator(items, 10)  # 10 items mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'items': page_obj,
        'total_items': items.count()
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'memory_bank/review_list_partial.html', context)

    return render(request, 'memory_bank/review_list.html', context)

@login_required
def memory_search(request):
    """Tìm kiếm ghi nhớ"""
    search_form = MemorySearchForm(request.user, request.GET)
    format_type = request.GET.get('format', '')
    items = MemoryItem.objects.filter(user=request.user)

    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        category = search_form.cleaned_data.get('category')
        priority = search_form.cleaned_data.get('priority')
        is_favorite = search_form.cleaned_data.get('is_favorite')

        if query:
            items = items.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__icontains=query)
            )

        if category:
            items = items.filter(category=category)

        if priority:
            items = items.filter(priority=priority)

        if is_favorite:
            items = items.filter(is_favorite=True)

    # Phân trang
    paginator = Paginator(items, 10)  # 10 items mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Đếm số ghi nhớ cần ôn tập hôm nay
    today = timezone.now()
    review_count = MemoryItem.objects.filter(
        user=request.user,
        next_review_date__lte=today
    ).count()

    context = {
        'search_form': search_form,
        'items': page_obj,
        'total_items': items.count(),
        'review_count': review_count
    }

    # Kiểm tra nếu là request HTMX partial
    if format_type == 'partial' or request.htmx:
        return render(request, 'memory_bank/search_results_partial.html', context)

    return render(request, 'memory_bank/search.html', context)
