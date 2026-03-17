import uuid
from django.db import models
from django.conf import settings


class Ticket(models.Model):
    """Ticket SAV créé par une pharmacie."""

    class TypeIntervention(models.TextChoices):
        EN_LIGNE = 'en_ligne', '🖥️ Assistance en ligne'
        SUR_SITE = 'sur_site', '🚗 Intervention sur site'

    class Categorie(models.TextChoices):
        LOGICIEL = 'logiciel', 'Logiciel'
        MATERIEL = 'materiel', 'Matériel'
        RESEAU = 'reseau', 'Réseau'
        AUTRE = 'autre', 'Autre'

    class Urgence(models.TextChoices):
        FAIBLE = 'faible', 'Faible'
        MOYEN = 'moyen', 'Moyen'
        CRITIQUE = 'critique', 'Critique'

    class Status(models.TextChoices):
        NOUVEAU = 'nouveau', 'Nouveau'
        ASSIGNE = 'assigne', 'Assigné'
        EN_COURS = 'en_cours', 'En cours'
        EN_ATTENTE = 'en_attente', 'En attente'
        RESOLU = 'resolu', 'Résolu'
        CLOTURE = 'cloture', 'Clôturé'

    # Identifiant unique lisible
    reference = models.CharField(
        'Référence', max_length=20, unique=True, editable=False,
    )
    objet = models.CharField('Objet du ticket', max_length=255)
    type_intervention = models.CharField(
        'Type d\'intervention', max_length=20,
        choices=TypeIntervention.choices,
    )
    categorie = models.CharField(
        'Catégorie', max_length=20, choices=Categorie.choices,
    )
    description = models.TextField('Description détaillée')
    urgence = models.CharField(
        'Niveau d\'urgence', max_length=20,
        choices=Urgence.choices, default=Urgence.MOYEN,
    )
    status = models.CharField(
        'Statut', max_length=20,
        choices=Status.choices, default=Status.NOUVEAU,
    )

    # Relations
    pharmacie = models.ForeignKey(
        'pharmacies.Pharmacie', on_delete=models.CASCADE,
        related_name='tickets', verbose_name='Pharmacie',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_tickets',
        verbose_name='Créé par',
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_tickets',
        verbose_name='Assigné à',
        limit_choices_to={'role': 'technicien'},
    )

    # WinDev sync
    windev_intervention_id = models.BigIntegerField(
        'IDIntervention WinDev', null=True, blank=True, unique=True,
    )
    windev_besoin_id = models.BigIntegerField(
        'IDBesoinsClient WinDev', null=True, blank=True, unique=True,
    )

    # Dates
    assigned_at = models.DateTimeField('Date assignation', null=True, blank=True)
    started_at = models.DateTimeField('Date début traitement', null=True, blank=True)
    resolved_at = models.DateTimeField('Date résolution', null=True, blank=True)
    closed_at = models.DateTimeField('Date clôture', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - {self.objet}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        super().save(*args, **kwargs)

    def _generate_reference(self):
        """Génère une référence unique : SAV-YYMM-NNNN (max 15 chars)."""
        from django.utils import timezone
        prefix = timezone.now().strftime('%y%m')
        full_prefix = f'SAV-{prefix}-'
        last = Ticket.objects.filter(
            reference__startswith=full_prefix
        ).order_by('-reference').first()
        if last:
            try:
                num = int(last.reference[len(full_prefix):]) + 1
            except (ValueError, IndexError):
                num = 1
        else:
            num = 1
        return f'SAV-{prefix}-{num:04d}'


class TicketAttachment(models.Model):
    """Pièce jointe d'un ticket."""
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name='attachments',
    )
    file = models.FileField(upload_to='tickets/attachments/%Y/%m/')
    filename = models.CharField('Nom du fichier', max_length=255)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pièce jointe'
        verbose_name_plural = 'Pièces jointes'

    def __str__(self):
        return self.filename


class TicketMessage(models.Model):
    """Message dans un ticket (échange pharmacie ↔ technicien)."""
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name='messages',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='ticket_messages',
    )
    content = models.TextField('Message')
    attachment = models.FileField(
        upload_to='tickets/messages/%Y/%m/', blank=True, null=True,
    )
    is_internal = models.BooleanField(
        'Note interne', default=False,
        help_text="Visible uniquement par les techniciens et admins",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']

    def __str__(self):
        return f"Message de {self.sender} sur {self.ticket.reference}"


class TicketStatusHistory(models.Model):
    """Historique des changements de statut."""
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name='status_history',
    )
    old_status = models.CharField('Ancien statut', max_length=20, blank=True)
    new_status = models.CharField('Nouveau statut', max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
    )
    comment = models.TextField('Commentaire', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Historique statut'
        verbose_name_plural = 'Historiques statuts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket.reference}: {self.old_status} → {self.new_status}"


class TicketDelegation(models.Model):
    """Historique des délégations de ticket."""
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name='delegations',
    )
    from_technicien = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='delegations_from',
    )
    to_technicien = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='delegations_to',
    )
    motif = models.TextField('Motif de la délégation')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Délégation'
        verbose_name_plural = 'Délégations'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket.reference}: {self.from_technicien} → {self.to_technicien}"


class TicketEvaluation(models.Model):
    """Évaluation du service par la pharmacie (optionnel)."""
    ticket = models.OneToOneField(
        Ticket, on_delete=models.CASCADE, related_name='evaluation',
    )
    note = models.PositiveSmallIntegerField('Note (1-5)')
    commentaire = models.TextField('Commentaire', blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Évaluation'
        verbose_name_plural = 'Évaluations'

    def __str__(self):
        return f"{self.ticket.reference}: {self.note}/5"
