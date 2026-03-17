from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.PharmacieViewSet, basename='pharmacie')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pharmacie_pk>/contacts/', views.ContactPharmacieViewSet.as_view({
        'get': 'list', 'post': 'create',
    })),
    path('<int:pharmacie_pk>/contacts/<int:pk>/', views.ContactPharmacieViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
    })),
    path('<int:pharmacie_pk>/equipements/', views.EquipementPharmacieViewSet.as_view({
        'get': 'list', 'post': 'create',
    })),
    path('<int:pharmacie_pk>/equipements/<int:pk>/', views.EquipementPharmacieViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
    })),
]
