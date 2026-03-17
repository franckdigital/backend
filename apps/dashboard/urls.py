from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('pharmacy/', views.PharmacyDashboardView.as_view(), name='pharmacy-dashboard'),
    path('technician/', views.TechnicianDashboardView.as_view(), name='technician-dashboard'),
    path('export/', views.ExportView.as_view(), name='export-tickets'),
]
