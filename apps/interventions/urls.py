from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.RapportInterventionViewSet, basename='rapport')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:rapport_pk>/photos/', views.PhotoInterventionViewSet.as_view({
        'get': 'list', 'post': 'create',
    })),
    path('<int:rapport_pk>/photos/<int:pk>/', views.PhotoInterventionViewSet.as_view({
        'delete': 'destroy',
    })),
]
