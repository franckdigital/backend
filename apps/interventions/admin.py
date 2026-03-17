from django.contrib import admin
from .models import RapportIntervention, PhotoIntervention


class PhotoInline(admin.TabularInline):
    model = PhotoIntervention
    extra = 0


@admin.register(RapportIntervention)
class RapportInterventionAdmin(admin.ModelAdmin):
    list_display = (
        'ticket', 'technicien', 'type_intervention', 'resultat',
        'temps_passe_minutes', 'distance_pharmacie_km', 'created_at',
    )
    list_filter = ('type_intervention', 'resultat')
    search_fields = ('ticket__reference', 'actions_realisees')
    inlines = [PhotoInline]
