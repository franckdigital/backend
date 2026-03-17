from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'logs', views.SyncLogViewSet, basename='sync-log')
router.register(r'cursors', views.SyncCursorViewSet, basename='sync-cursor')

urlpatterns = [
    path('', include(router.urls)),
    path('status/', views.SyncStatusView.as_view(), name='sync-status'),
    path('sync/windev-to-django/', views.SyncWindevToDjangoView.as_view(), name='sync-windev-to-django'),
    path('sync/django-to-windev/', views.SyncDjangoToWindevView.as_view(), name='sync-django-to-windev'),
    path('sync/full/', views.FullSyncView.as_view(), name='sync-full'),
]
