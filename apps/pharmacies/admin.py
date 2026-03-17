from django.contrib import admin
from .models import Pharmacie, ContactPharmacie, EquipementPharmacie


class ContactInline(admin.TabularInline):
    model = ContactPharmacie
    extra = 0


class EquipementInline(admin.TabularInline):
    model = EquipementPharmacie
    extra = 0


@admin.register(Pharmacie)
class PharmacieAdmin(admin.ModelAdmin):
    list_display = ('nom_pharmacie', 'code_2st', 'ville', 'nom_responsable', 'sous_contrat')
    list_filter = ('sous_contrat', 'commune__region', 'ville')
    search_fields = ('nom_pharmacie', 'code_2st', 'nom_responsable')
    inlines = [ContactInline, EquipementInline]
