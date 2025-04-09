from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import NoteIntegrationAccount, SyncedNote
from .services import NoteIntegrationService
from memory_bank.models import MemoryItem


@login_required
def integration_home(request):
    """Trang chủ tích hợp công cụ ghi chú"""
    accounts = NoteIntegrationAccount.objects.filter(user=request.user)
    synced_notes = SyncedNote.objects.filter(user=request.user).order_by('-last_synced_at')[:10]
    
    context = {
        'accounts': accounts,
        'synced_notes': synced_notes,
    }
    
    return render(request, 'note_integration_app/home.html', context)


@login_required
def connect_account(request, provider):
    """Kết nối tài khoản mới"""
    try:
        # Kiểm tra xem provider có được hỗ trợ không
        if provider not in [choice[0] for choice in NoteIntegrationAccount.PROVIDER_CHOICES]:
            messages.error(request, f"Provider '{provider}' không được hỗ trợ.")
            return redirect('note_integration_home')
        
        # Kiểm tra xem đã có tài khoản cho provider này chưa
        if NoteIntegrationAccount.objects.filter(user=request.user, provider=provider).exists():
            messages.warning(request, f"Bạn đã kết nối tài khoản {provider}. Vui lòng ngắt kết nối trước khi kết nối lại.")
            return redirect('note_integration_home')
        
        # Lấy URL xác thực
        auth_url = NoteIntegrationService.get_auth_url(provider)
        
        # Lưu provider vào session để sử dụng trong callback
        request.session['integration_provider'] = provider
        
        # Chuyển hướng đến trang xác thực
        return redirect(auth_url)
    
    except Exception as e:
        messages.error(request, f"Lỗi khi kết nối tài khoản: {str(e)}")
        return redirect('note_integration_home')


@login_required
def auth_callback(request):
    """Callback sau khi xác thực"""
    try:
        # Lấy provider từ session
        provider = request.session.get('integration_provider')
        if not provider:
            messages.error(request, "Không tìm thấy thông tin provider. Vui lòng thử lại.")
            return redirect('note_integration_home')
        
        # Lấy code từ query params
        code = request.GET.get('code')
        if not code:
            messages.error(request, "Không tìm thấy code xác thực. Vui lòng thử lại.")
            return redirect('note_integration_home')
        
        # Đổi code lấy token
        token_info = NoteIntegrationService.exchange_code_for_token(provider, code)
        
        # Lưu thông tin tài khoản
        account = NoteIntegrationAccount.objects.create(
            user=request.user,
            provider=provider,
            access_token=token_info['access_token'],
            refresh_token=token_info.get('refresh_token'),
            token_expires_at=token_info.get('expires_at'),
            account_info=token_info.get('account_info')
        )
        
        messages.success(request, f"Kết nối tài khoản {provider} thành công!")
        
        # Xóa provider khỏi session
        if 'integration_provider' in request.session:
            del request.session['integration_provider']
        
        return redirect('note_integration_home')
    
    except Exception as e:
        messages.error(request, f"Lỗi khi xác thực tài khoản: {str(e)}")
        return redirect('note_integration_home')


@login_required
def disconnect_account(request, account_id):
    """Ngắt kết nối tài khoản"""
    try:
        account = NoteIntegrationAccount.objects.get(id=account_id, user=request.user)
        provider_name = account.get_provider_display()
        
        # Xóa tất cả các ghi chú đã đồng bộ
        SyncedNote.objects.filter(integration_account=account).delete()
        
        # Xóa tài khoản
        account.delete()
        
        messages.success(request, f"Đã ngắt kết nối tài khoản {provider_name}.")
    except NoteIntegrationAccount.DoesNotExist:
        messages.error(request, "Không tìm thấy tài khoản.")
    
    return redirect('note_integration_home')


@login_required
def account_details(request, account_id):
    """Xem chi tiết tài khoản"""
    try:
        account = NoteIntegrationAccount.objects.get(id=account_id, user=request.user)
        synced_notes = SyncedNote.objects.filter(integration_account=account).order_by('-last_synced_at')
        
        # Lấy thông tin từ dịch vụ
        service = NoteIntegrationService.get_service(account.provider, account.access_token)
        
        if account.provider == 'notion':
            databases = service.get_databases()
            context = {
                'account': account,
                'synced_notes': synced_notes,
                'databases': databases,
            }
        
        elif account.provider == 'onenote':
            notebooks = service.get_notebooks()
            context = {
                'account': account,
                'synced_notes': synced_notes,
                'notebooks': notebooks,
            }
        
        else:
            context = {
                'account': account,
                'synced_notes': synced_notes,
            }
        
        return render(request, f'note_integration_app/{account.provider}_details.html', context)
    
    except NoteIntegrationAccount.DoesNotExist:
        messages.error(request, "Không tìm thấy tài khoản.")
        return redirect('note_integration_home')
    except Exception as e:
        messages.error(request, f"Lỗi khi lấy thông tin tài khoản: {str(e)}")
        return redirect('note_integration_home')


@login_required
@require_POST
def sync_note(request):
    """Đồng bộ ghi chú"""
    try:
        account_id = request.POST.get('account_id')
        memory_item_id = request.POST.get('memory_item_id')
        
        if not account_id or not memory_item_id:
            return JsonResponse({'success': False, 'error': 'Thiếu thông tin cần thiết.'})
        
        # Lấy tài khoản và ghi chú
        account = NoteIntegrationAccount.objects.get(id=account_id, user=request.user)
        memory_item = MemoryItem.objects.get(id=memory_item_id, user=request.user)
        
        # Kiểm tra xem ghi chú đã được đồng bộ chưa
        existing_sync = SyncedNote.objects.filter(
            user=request.user,
            integration_account=account,
            memory_item_id=memory_item_id
        ).first()
        
        if existing_sync:
            # Cập nhật ghi chú đã có
            service = NoteIntegrationService.get_service(account.provider, account.access_token)
            
            if account.provider == 'notion':
                service.update_page(
                    existing_sync.external_id,
                    title=memory_item.title,
                    content=memory_item.content
                )
            
            elif account.provider == 'onenote':
                service.update_page(
                    existing_sync.external_id,
                    content=memory_item.content
                )
            
            # Cập nhật thời gian đồng bộ
            existing_sync.last_synced_at = timezone.now()
            existing_sync.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Đã cập nhật ghi chú thành công.',
                'is_update': True,
                'external_url': existing_sync.external_url
            })
        
        else:
            # Tạo ghi chú mới
            service = NoteIntegrationService.get_service(account.provider, account.access_token)
            
            if account.provider == 'notion':
                # Lấy database_id từ request
                database_id = request.POST.get('database_id')
                if not database_id:
                    return JsonResponse({'success': False, 'error': 'Thiếu database_id.'})
                
                # Tạo trang mới
                result = service.create_page(
                    database_id=database_id,
                    title=memory_item.title,
                    content=memory_item.content
                )
                
                # Lưu thông tin đồng bộ
                synced_note = SyncedNote.objects.create(
                    user=request.user,
                    integration_account=account,
                    memory_item_id=memory_item_id,
                    external_id=result['id'],
                    external_url=result.get('url', ''),
                    title=memory_item.title
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Đã đồng bộ ghi chú thành công.',
                    'is_update': False,
                    'external_url': synced_note.external_url
                })
            
            elif account.provider == 'onenote':
                # Lấy section_id từ request
                section_id = request.POST.get('section_id')
                if not section_id:
                    return JsonResponse({'success': False, 'error': 'Thiếu section_id.'})
                
                # Tạo trang mới
                result = service.create_page(
                    section_id=section_id,
                    title=memory_item.title,
                    content=memory_item.content
                )
                
                # Lưu thông tin đồng bộ
                synced_note = SyncedNote.objects.create(
                    user=request.user,
                    integration_account=account,
                    memory_item_id=memory_item_id,
                    external_id=result['id'],
                    external_url=result.get('url', ''),
                    title=memory_item.title
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Đã đồng bộ ghi chú thành công.',
                    'is_update': False,
                    'external_url': synced_note.external_url
                })
            
            else:
                return JsonResponse({'success': False, 'error': f"Provider '{account.provider}' không được hỗ trợ."})
    
    except NoteIntegrationAccount.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy tài khoản.'})
    except MemoryItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy ghi chú.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f"Lỗi khi đồng bộ ghi chú: {str(e)}"})


@login_required
@require_POST
def get_sections(request):
    """Lấy danh sách sections trong notebook (OneNote)"""
    try:
        account_id = request.POST.get('account_id')
        notebook_id = request.POST.get('notebook_id')
        
        if not account_id or not notebook_id:
            return JsonResponse({'success': False, 'error': 'Thiếu thông tin cần thiết.'})
        
        # Lấy tài khoản
        account = NoteIntegrationAccount.objects.get(id=account_id, user=request.user)
        
        if account.provider != 'onenote':
            return JsonResponse({'success': False, 'error': 'Chỉ hỗ trợ OneNote.'})
        
        # Lấy danh sách sections
        service = NoteIntegrationService.get_service(account.provider, account.access_token)
        sections = service.get_sections(notebook_id)
        
        return JsonResponse({
            'success': True,
            'sections': sections
        })
    
    except NoteIntegrationAccount.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy tài khoản.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f"Lỗi khi lấy danh sách sections: {str(e)}"})
