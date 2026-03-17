from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Notification pour les utilisateurs."""

    class Type(models.TextChoices):
        TICKET_CREATED = 'ticket_created', 'Nouveau ticket'
        TICKET_ASSIGNED = 'ticket_assigned', 'Ticket assigné'
        TICKET_UPDATED = 'ticket_updated', 'Ticket mis à jour'
        TICKET_RESOLVED = 'ticket_resolved', 'Ticket résolu'
        TICKET_DELEGATED = 'ticket_delegated', 'Ticket délégué'
        MESSAGE_RECEIVED = 'message_received', 'Nouveau message'
        ACCOUNT_VALIDATED = 'account_validated', 'Compte validé'
        REPORT_SUBMITTED = 'report_submitted', 'Rapport soumis'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications', verbose_name='Destinataire',
    )
    type = models.CharField('Type', max_length=30, choices=Type.choices)
    title = models.CharField('Titre', max_length=255)
    message = models.TextField('Message')
    is_read = models.BooleanField('Lu', default=False)
    link = models.CharField('Lien', max_length=500, blank=True,
                            help_text="URL relative vers la ressource concernée")
    ticket = models.ForeignKey(
        'tickets.Ticket', on_delete=models.CASCADE,
        null=True, blank=True, related_name='notifications',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} → {self.recipient.username}"
