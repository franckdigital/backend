"""Service de création de notifications."""
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification


def notify(recipient, type, title, message, ticket=None, link=''):
    """Créer une notification et envoyer un email."""
    notif = Notification.objects.create(
        recipient=recipient,
        type=type,
        title=title,
        message=message,
        ticket=ticket,
        link=link,
    )
    # Email (non bloquant, échoue silencieusement)
    try:
        if recipient.email:
            send_mail(
                subject=f"[SAV Pharmacie] {title}",
                message=message,
                from_email=settings.EMAIL_HOST_USER or 'noreply@sav-pharmacie.com',
                recipient_list=[recipient.email],
                fail_silently=True,
            )
    except Exception:
        pass
    return notif


def notify_ticket_created(ticket):
    """Notifier l'admin et le technicien assigné d'un nouveau ticket."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    msg = f"Nouveau ticket {ticket.reference}: {ticket.objet} (Urgence: {ticket.get_urgence_display()})"

    # Notifier les admins
    for admin in User.objects.filter(role='admin', is_active=True):
        notify(admin, 'ticket_created', 'Nouveau ticket SAV', msg, ticket=ticket)

    # Notifier le technicien assigné
    if ticket.assigned_to:
        notify(
            ticket.assigned_to,
            'ticket_assigned',
            'Ticket assigné',
            f"Le ticket {ticket.reference} vous a été assigné: {ticket.objet}",
            ticket=ticket,
        )


def notify_ticket_status_changed(ticket, old_status, new_status, changed_by):
    """Notifier les parties concernées d'un changement de statut."""
    msg = f"Le ticket {ticket.reference} est passé de '{old_status}' à '{new_status}'."

    # Notifier la pharmacie
    if ticket.pharmacie and ticket.pharmacie.user:
        notify(
            ticket.pharmacie.user,
            'ticket_updated',
            f"Ticket {ticket.reference} mis à jour",
            msg,
            ticket=ticket,
        )

    # Notifier le technicien si ce n'est pas lui qui a changé
    if ticket.assigned_to and ticket.assigned_to != changed_by:
        notify(ticket.assigned_to, 'ticket_updated', f"Ticket {ticket.reference} mis à jour", msg, ticket=ticket)


def notify_new_message(ticket_message):
    """Notifier le destinataire d'un nouveau message."""
    ticket = ticket_message.ticket
    sender = ticket_message.sender

    # Notifier la pharmacie si c'est le technicien qui écrit
    if sender.is_technicien and ticket.pharmacie and ticket.pharmacie.user:
        notify(
            ticket.pharmacie.user,
            'message_received',
            f"Nouveau message sur {ticket.reference}",
            f"{sender.get_full_name()} a envoyé un message sur le ticket {ticket.reference}.",
            ticket=ticket,
        )
    # Notifier le technicien si c'est la pharmacie qui écrit
    elif sender.is_pharmacie and ticket.assigned_to:
        notify(
            ticket.assigned_to,
            'message_received',
            f"Nouveau message sur {ticket.reference}",
            f"La pharmacie a envoyé un message sur le ticket {ticket.reference}.",
            ticket=ticket,
        )
