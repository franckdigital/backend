from django.db import models
from django.conf import settings


class Region(models.Model):
    """Région géographique."""
    name = models.CharField('Nom', max_length=100, unique=True)
    code = models.CharField('Code', max_length=10, unique=True)
    is_active = models.BooleanField('Actif', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Région'
        verbose_name_plural = 'Régions'
        ordering = ['name']

    def __str__(self):
        return self.name


class Commune(models.Model):
    """Commune dans une région."""
    name = models.CharField('Nom', max_length=100)
    code = models.CharField('Code', max_length=10, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='communes')
    is_active = models.BooleanField('Actif', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Commune'
        verbose_name_plural = 'Communes'
        ordering = ['region__name', 'name']
        unique_together = ['name', 'region']

    def __str__(self):
        return f"{self.name} ({self.region.name})"


class Quartier(models.Model):
    """Quartier dans une commune."""
    name = models.CharField('Nom', max_length=100)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, related_name='quartiers')
    is_active = models.BooleanField('Actif', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Quartier'
        verbose_name_plural = 'Quartiers'
        ordering = ['commune__name', 'name']
        unique_together = ['name', 'commune']

    def __str__(self):
        return f"{self.name} ({self.commune.name})"


class Zone(models.Model):
    """Zone de couverture (ensemble de communes/quartiers)."""
    name = models.CharField('Nom de la zone', max_length=100, unique=True)
    description = models.TextField('Description', blank=True)
    regions = models.ManyToManyField(Region, blank=True, related_name='zones')
    communes = models.ManyToManyField(Commune, blank=True, related_name='zones')
    quartiers = models.ManyToManyField(Quartier, blank=True, related_name='zones')
    is_active = models.BooleanField('Actif', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Zone'
        verbose_name_plural = 'Zones'
        ordering = ['name']

    def __str__(self):
        return self.name


class TechnicienProfile(models.Model):
    """Profil technicien avec zones et compétences."""

    class Competence(models.TextChoices):
        LOGICIEL = 'logiciel', 'Logiciel'
        MATERIEL = 'materiel', 'Matériel'
        RESEAU = 'reseau', 'Réseau'
        TOUS = 'tous', 'Tous'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='technicien_profile',
        limit_choices_to={'role': 'technicien'},
    )
    zones = models.ManyToManyField(Zone, blank=True, related_name='techniciens')
    competences = models.CharField(
        'Compétence principale',
        max_length=20,
        choices=Competence.choices,
        default=Competence.TOUS,
    )
    max_tickets_simultanes = models.PositiveIntegerField(
        'Max tickets simultanés', default=5
    )
    is_available = models.BooleanField('Disponible', default=True)
    latitude = models.DecimalField(
        'Latitude', max_digits=10, decimal_places=7, null=True, blank=True
    )
    longitude = models.DecimalField(
        'Longitude', max_digits=10, decimal_places=7, null=True, blank=True
    )
    last_location_update = models.DateTimeField(
        'Dernière MAJ position', null=True, blank=True
    )

    # WinDev sync
    windev_technicien_id = models.BigIntegerField(
        'ID Technicien WinDev', null=True, blank=True, unique=True,
    )

    class Meta:
        verbose_name = 'Profil technicien'
        verbose_name_plural = 'Profils techniciens'

    def __str__(self):
        return f"Technicien: {self.user.get_full_name()}"

    @property
    def active_tickets_count(self):
        """Nombre de tickets en cours."""
        return self.user.assigned_tickets.filter(
            status__in=['assigne', 'en_cours', 'en_attente']
        ).count()

    @property
    def is_overloaded(self):
        """Le technicien a-t-il atteint sa capacité max ?"""
        return self.active_tickets_count >= self.max_tickets_simultanes
