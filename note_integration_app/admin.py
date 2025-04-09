from django.contrib import admin
from .models import NoteIntegrationAccount, SyncedNote


@admin.register(NoteIntegrationAccount)
class NoteIntegrationAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'created_at', 'updated_at')
    list_filter = ('provider', 'created_at')
    search_fields = ('user__username', 'provider')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SyncedNote)
class SyncedNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'integration_account', 'last_synced_at')
    list_filter = ('integration_account__provider', 'last_synced_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('created_at', 'last_synced_at')
