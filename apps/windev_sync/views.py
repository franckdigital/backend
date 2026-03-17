from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import SyncLog, SyncCursor
from .serializers import SyncLogSerializer, SyncCursorSerializer
from .tasks import (
    sync_windev_to_django_incremental,
    sync_django_to_windev_incremental,
    sync_windev_referentials,
    sync_full,
)
from .services import run_full_sync
from apps.accounts.permissions import IsAdmin


class SyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Historique des synchronisations WinDev ↔ Django."""
    queryset = SyncLog.objects.all()
    serializer_class = SyncLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['direction', 'entity_type', 'status']
    ordering_fields = ['created_at']

    @extend_schema(tags=['WinDev Sync'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=['WinDev Sync'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class SyncCursorViewSet(viewsets.ReadOnlyModelViewSet):
    """État des curseurs de synchronisation incrémentale."""
    queryset = SyncCursor.objects.all()
    serializer_class = SyncCursorSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(tags=['WinDev Sync'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=['WinDev Sync'])
    @action(detail=False, methods=['post'])
    def reset(self, request):
        """Réinitialiser tous les curseurs (force une re-sync complète)."""
        SyncCursor.objects.all().update(last_synced_id=0, last_synced_at=None)
        return Response({'detail': 'Curseurs réinitialisés.'})


class SyncWindevToDjangoView(APIView):
    """Déclencher manuellement : WinDev → Django (incrémental)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(tags=['WinDev Sync'])
    def post(self, request):
        mode = request.data.get('mode', 'async')
        if mode == 'sync':
            from .services import run_windev_to_django_incremental
            try:
                result = run_windev_to_django_incremental()
                return Response(result)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            task = sync_windev_to_django_incremental.delay()
            return Response({
                'detail': 'Synchronisation WinDev → Django lancée en arrière-plan.',
                'task_id': task.id,
            }, status=status.HTTP_202_ACCEPTED)


class SyncDjangoToWindevView(APIView):
    """Déclencher manuellement : Django → WinDev (incrémental)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(tags=['WinDev Sync'])
    def post(self, request):
        mode = request.data.get('mode', 'async')
        if mode == 'sync':
            from .services import run_django_to_windev_incremental
            try:
                result = run_django_to_windev_incremental()
                return Response(result)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            task = sync_django_to_windev_incremental.delay()
            return Response({
                'detail': 'Synchronisation Django → WinDev lancée en arrière-plan.',
                'task_id': task.id,
            }, status=status.HTTP_202_ACCEPTED)


class FullSyncView(APIView):
    """Synchronisation complète bidirectionnelle."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(tags=['WinDev Sync'])
    def post(self, request):
        mode = request.data.get('mode', 'async')
        if mode == 'sync':
            try:
                result = run_full_sync()
                return Response(result)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            task = sync_full.delay()
            return Response({
                'detail': 'Synchronisation complète bidirectionnelle lancée en arrière-plan.',
                'task_id': task.id,
            }, status=status.HTTP_202_ACCEPTED)


class SyncStatusView(APIView):
    """Vue d'ensemble de l'état de la synchronisation."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(tags=['WinDev Sync'])
    def get(self, request):
        cursors = {}
        for sc in SyncCursor.objects.all():
            cursors[sc.entity_type] = {
                'direction': sc.direction,
                'last_synced_id': sc.last_synced_id,
                'last_synced_at': sc.last_synced_at,
            }

        last_logs = {}
        for direction in ['windev_to_web', 'web_to_windev']:
            log = SyncLog.objects.filter(direction=direction).first()
            if log:
                last_logs[direction] = {
                    'entity_type': log.entity_type,
                    'status': log.status,
                    'records_synced': log.records_synced,
                    'records_failed': log.records_failed,
                    'completed_at': log.completed_at,
                }

        return Response({
            'cursors': cursors,
            'last_sync': last_logs,
            'total_logs': SyncLog.objects.count(),
            'failed_count': SyncLog.objects.filter(status='failed').count(),
        })
