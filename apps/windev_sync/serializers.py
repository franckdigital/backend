from rest_framework import serializers
from .models import SyncLog, SyncCursor


class SyncLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncLog
        fields = (
            'id', 'direction', 'entity_type', 'records_synced',
            'records_failed', 'status', 'error_details',
            'started_at', 'completed_at', 'created_at',
        )


class SyncCursorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncCursor
        fields = (
            'id', 'entity_type', 'direction',
            'last_synced_id', 'last_synced_at', 'updated_at',
        )
