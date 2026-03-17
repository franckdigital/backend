from django.contrib import admin
from .models import Region, Commune, Quartier, Zone, TechnicienProfile


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    search_fields = ('name', 'code')


@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'region', 'is_active')
    list_filter = ('region', 'is_active')
    search_fields = ('name', 'code')


@admin.register(Quartier)
class QuartierAdmin(admin.ModelAdmin):
    list_display = ('name', 'commune', 'is_active')
    list_filter = ('commune__region', 'is_active')
    search_fields = ('name',)


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    filter_horizontal = ('regions', 'communes', 'quartiers')
    search_fields = ('name',)


@admin.register(TechnicienProfile)
class TechnicienProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'competences', 'is_available', 'max_tickets_simultanes')
    list_filter = ('is_available', 'competences')
    filter_horizontal = ('zones',)
    search_fields = ('user__first_name', 'user__last_name')
