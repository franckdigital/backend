from django.db import models
from django.conf import settings


class Pharmacie(models.Model):
    """Profil pharmacie lié à un utilisateur."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pharmacie_profile',
        limit_choices_to={'role': 'pharmacie'},
    )
    nom_pharmacie = models.CharField('Nom de la pharmacie', max_length=150)
    code_2st = models.CharField('Code 2ST', max_length=10, blank=True)
    adresse = models.CharField('Adresse', max_length=255, blank=True)
    ville = models.CharField('Ville', max_length=100, blank=True)
    commune = models.ForeignKey(
        'zones.Commune', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='pharmacies',
    )
    quartier = models.ForeignKey(
        'zones.Quartier', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='pharmacies',
    )
    latitude = models.DecimalField(
        'Latitude', max_digits=10, decimal_places=7, null=True, blank=True
    )
    longitude = models.DecimalField(
        'Longitude', max_digits=10, decimal_places=7, null=True, blank=True
    )
    nom_responsable = models.CharField('Nom du responsable', max_length=100, blank=True)
    tel_responsable = models.CharField('Tél. responsable', max_length=20, blank=True)
    email_pharmacie = models.EmailField('Email pharmacie', blank=True)
    logo = models.ImageField(upload_to='pharmacies/logos/', blank=True, null=True)
    sous_contrat = models.BooleanField('Sous contrat', default=False)
    date_contrat = models.DateField('Date contrat', null=True, blank=True)
    interieur_pays = models.BooleanField('Intérieur du pays', default=False)
    date_maintenance = models.DateField('Date maintenance', null=True, blank=True)
    notes = models.TextField('Notes', blank=True)

    # WinDev sync
    windev_client_id = models.BigIntegerField(
        'IDClient WinDev', null=True, blank=True, unique=True,
        help_text="IDClient dans T_Client WinDev"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pharmacie'
        verbose_name_plural = 'Pharmacies'
        ordering = ['nom_pharmacie']

    def __str__(self):
        return self.nom_pharmacie


class ContactPharmacie(models.Model):
    """Contacts supplémentaires d'une pharmacie."""
    pharmacie = models.ForeignKey(
        Pharmacie, on_delete=models.CASCADE, related_name='contacts'
    )
    nom = models.CharField('Nom', max_length=100)
    fonction = models.CharField('Fonction', max_length=100, blank=True)
    telephone = models.CharField('Téléphone', max_length=20)
    email = models.EmailField('Email', blank=True)

    class Meta:
        verbose_name = 'Contact pharmacie'
        verbose_name_plural = 'Contacts pharmacie'

    def __str__(self):
        return f"{self.nom} - {self.pharmacie.nom_pharmacie}"


class EquipementPharmacie(models.Model):
    """Équipements installés dans une pharmacie (pour référence SAV)."""

    class TypeEquipement(models.TextChoices):
        LOGICIEL = 'logiciel', 'Logiciel'
        MATERIEL = 'materiel', 'Matériel'
        RESEAU = 'reseau', 'Réseau'
        AUTRE = 'autre', 'Autre'

    pharmacie = models.ForeignKey(
        Pharmacie, on_delete=models.CASCADE, related_name='equipements'
    )
    nom = models.CharField('Nom', max_length=150)
    type_equipement = models.CharField(
        'Type', max_length=20, choices=TypeEquipement.choices
    )
    numero_serie = models.CharField('N° série', max_length=100, blank=True)
    date_installation = models.DateField('Date installation', null=True, blank=True)
    description = models.TextField('Description', blank=True)
    is_active = models.BooleanField('Actif', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Équipement'
        verbose_name_plural = 'Équipements'
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.pharmacie.nom_pharmacie})"
