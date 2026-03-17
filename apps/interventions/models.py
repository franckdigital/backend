from django.db import models
from django.conf import settings


class RapportIntervention(models.Model):
    """Rapport d'intervention rempli par le technicien."""

    class TypeIntervention(models.TextChoices):
        A_DISTANCE = 'a_distance', 'À distance'
        SUR_SITE = 'sur_site', 'Sur site'

    class Resultat(models.TextChoices):
        RESOLU = 'resolu', 'Résolu'
        PARTIELLEMENT = 'partiellement', 'Partiellement résolu'
        NON_RESOLU = 'non_resolu', 'Non résolu'
        EN_ATTENTE_PIECE = 'en_attente_piece', 'En attente pièce/matériel'

    ticket = models.ForeignKey(
        'tickets.Ticket', on_delete=models.CASCADE,
        related_name='rapports', verbose_name='Ticket',
    )
    technicien = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='rapports_intervention',
        verbose_name='Technicien',
    )
    type_intervention = models.CharField(
        'Type d\'intervention', max_length=20,
        choices=TypeIntervention.choices,
    )
    actions_realisees = models.TextField('Actions réalisées')
    resultat = models.CharField(
        'Résultat', max_length=30, choices=Resultat.choices,
    )
    temps_passe_minutes = models.PositiveIntegerField(
        'Temps passé (minutes)', default=0,
    )
    recommandations = models.TextField('Recommandations', blank=True)
    signature_numerique = models.ImageField(
        upload_to='interventions/signatures/%Y/%m/',
        blank=True, null=True, verbose_name='Signature numérique',
    )

    # Géolocalisation automatique lors de la sauvegarde (sur site)
    latitude = models.DecimalField(
        'Latitude', max_digits=10, decimal_places=7, null=True, blank=True,
    )
    longitude = models.DecimalField(
        'Longitude', max_digits=10, decimal_places=7, null=True, blank=True,
    )
    distance_pharmacie_km = models.DecimalField(
        'Distance pharmacie (km)', max_digits=8, decimal_places=2,
        null=True, blank=True,
    )
    geolocation_datetime = models.DateTimeField(
        'Date/heure géolocalisation', null=True, blank=True,
    )

    # WinDev sync
    windev_detail_intervention_id = models.BigIntegerField(
        'IDDetailIntervention WinDev', null=True, blank=True, unique=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rapport d\'intervention'
        verbose_name_plural = 'Rapports d\'intervention'
        ordering = ['-created_at']

    def __str__(self):
        return f"Rapport {self.ticket.reference} - {self.get_resultat_display()}"


class PhotoIntervention(models.Model):
    """Photos prises pendant l'intervention."""
    rapport = models.ForeignKey(
        RapportIntervention, on_delete=models.CASCADE, related_name='photos',
    )
    image = models.ImageField(upload_to='interventions/photos/%Y/%m/')
    description = models.CharField('Description', max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Photo intervention'
        verbose_name_plural = 'Photos intervention'

    def __str__(self):
        return f"Photo - {self.rapport.ticket.reference}"
