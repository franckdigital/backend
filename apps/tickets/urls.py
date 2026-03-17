from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.TicketViewSet, basename='ticket')

urlpatterns = [
    path('', include(router.urls)),
    # Messages imbriqués dans un ticket
    path('<int:ticket_pk>/messages/', views.TicketMessageViewSet.as_view({
        'get': 'list', 'post': 'create',
    })),
    # Pièces jointes imbriquées dans un ticket
    path('<int:ticket_pk>/attachments/', views.TicketAttachmentViewSet.as_view({
        'get': 'list', 'post': 'create',
    })),
    path('<int:ticket_pk>/attachments/<int:pk>/', views.TicketAttachmentViewSet.as_view({
        'delete': 'destroy',
    })),
]
