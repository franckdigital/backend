from django.contrib import admin
from .models import SyncLog, SyncCursor


@admin.register(SyncCursor)
class SyncCursorAdmin(admin.ModelAdmin):
    list_display = ('entity_type', 'direction', 'last_synced_id', 'last_synced_at', 'updated_at')
    list_filter = ('direction',)
    readonly_fields = ('updated_at',)


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ('entity_type', 'direction', 'status', 'records_synced', 'records_failed', 'created_at')
    list_filter = ('direction', 'status', 'entity_type')
    readonly_fields = ('created_at',)
