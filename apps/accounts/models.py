from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_validated', True)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    objects = CustomUserManager()
    """Custom user model with roles for SAV system."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrateur'
        PHARMACIE = 'pharmacie', 'Pharmacie'
        TECHNICIEN = 'technicien', 'Technicien SAV'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PHARMACIE,
    )
    phone = models.CharField('Téléphone', max_length=20, blank=True)
    phone2 = models.CharField('Téléphone 2', max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_validated = models.BooleanField('Compte validé', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # WinDev sync field
    windev_user_id = models.BigIntegerField(
        'ID Utilisateur WinDev', null=True, blank=True, unique=True,
        help_text="IDUtilisateur dans T_Utilisateur WinDev"
    )

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_pharmacie(self):
        return self.role == self.Role.PHARMACIE

    @property
    def is_technicien(self):
        return self.role == self.Role.TECHNICIEN
