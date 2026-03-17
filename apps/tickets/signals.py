from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ticket, TicketStatusHistory


@receiver(post_save, sender=Ticket)
def track_status_change(sender, instance, created, **kwargs):
    """Enregistre l'historique des changements de statut."""
    if created:
        TicketStatusHistory.objects.create(
            ticket=instance,
            old_status='',
            new_status=instance.status,
            changed_by=instance.created_by,
            comment='Ticket créé',
        )
