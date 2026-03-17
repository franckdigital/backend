from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'techniciens', views.TechnicienProfileViewSet, basename='technicien-profile')
router.register(r'regions', views.RegionViewSet, basename='region')
router.register(r'communes', views.CommuneViewSet, basename='commune')
router.register(r'quartiers', views.QuartierViewSet, basename='quartier')
router.register(r'', views.ZoneViewSet, basename='zone')

urlpatterns = [
    path('', include(router.urls)),
]
