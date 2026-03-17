from django.db import models


class SyncCursor(models.Model):
    """
    Curseur de synchronisation incrémentale.
    Stocke le dernier ID ou date synchronisé pour chaque entité/direction
    afin de ne traiter que les nouveaux enregistrements à chaque cycle.
    """
    entity_type = models.CharField('Type d\'entité', max_length=50, unique=True)
    direction = models.CharField('Direction', max_length=20)
    last_synced_id = models.BigIntegerField('Dernier ID synchronisé', default=0)
    last_synced_at = models.DateTimeField('Dernière sync réussie', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Curseur de synchronisation'
        verbose_name_plural = 'Curseurs de synchronisation'

    def __str__(self):
        return f"{self.entity_type} ({self.direction}) → ID {self.last_synced_id}"


class SyncLog(models.Model):
    """Log de synchronisation avec la base WinDev."""

    class Direction(models.TextChoices):
        WINDEV_TO_WEB = 'windev_to_web', 'WinDev → Web'
        WEB_TO_WINDEV = 'web_to_windev', 'Web → WinDev'

    class Status(models.TextChoices):
        SUCCESS = 'success', 'Succès'
        PARTIAL = 'partial', 'Partiel'
        FAILED = 'failed', 'Échec'

    direction = models.CharField('Direction', max_length=20, choices=Direction.choices)
    entity_type = models.CharField('Type d\'entité', max_length=50,
                                   help_text="Ex: client, intervention, utilisateur")
    records_synced = models.PositiveIntegerField('Enregistrements synchronisés', default=0)
    records_failed = models.PositiveIntegerField('Enregistrements échoués', default=0)
    status = models.CharField('Statut', max_length=20, choices=Status.choices)
    error_details = models.TextField('Détails erreurs', blank=True)
    started_at = models.DateTimeField('Début')
    completed_at = models.DateTimeField('Fin', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log de synchronisation'
        verbose_name_plural = 'Logs de synchronisation'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.entity_type} ({self.direction}) - {self.status}"
