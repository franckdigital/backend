from rest_framework import serializers
from django.db import models
from django.utils import timezone

from .models import (
    Ticket, TicketAttachment, TicketMessage,
    TicketStatusHistory, TicketDelegation, TicketEvaluation,
)
from apps.accounts.serializers import UserSerializer


class TicketAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAttachment
        fields = ('id', 'file', 'filename', 'uploaded_by', 'created_at')
        read_only_fields = ('id', 'uploaded_by', 'created_at')

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        if not validated_data.get('filename') and validated_data.get('file'):
            validated_data['filename'] = validated_data['file'].name
        return super().create(validated_data)


class TicketMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_role = serializers.CharField(source='sender.role', read_only=True)

    class Meta:
        model = TicketMessage
        fields = (
            'id', 'ticket', 'sender', 'sender_name', 'sender_role',
            'content', 'attachment', 'is_internal', 'created_at',
        )
        read_only_fields = ('id', 'sender', 'sender_name', 'sender_role', 'created_at')

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class TicketStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)

    class Meta:
        model = TicketStatusHistory
        fields = (
            'id', 'old_status', 'new_status', 'changed_by',
            'changed_by_name', 'comment', 'created_at',
        )
        read_only_fields = ('id', 'created_at')


class TicketDelegationSerializer(serializers.ModelSerializer):
    from_name = serializers.CharField(source='from_technicien.get_full_name', read_only=True)
    to_name = serializers.CharField(source='to_technicien.get_full_name', read_only=True)

    class Meta:
        model = TicketDelegation
        fields = (
            'id', 'ticket', 'from_technicien', 'from_name',
            'to_technicien', 'to_name', 'motif', 'created_at',
        )
        read_only_fields = ('id', 'from_technicien', 'from_name', 'created_at')


class TicketEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketEvaluation
        fields = ('id', 'ticket', 'note', 'commentaire', 'created_by', 'created_at')
        read_only_fields = ('id', 'created_by', 'created_at')

    def validate_note(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La note doit être entre 1 et 5.")
        return value

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TicketListSerializer(serializers.ModelSerializer):
    """Serializer léger pour la liste des tickets."""
    pharmacie_name = serializers.CharField(source='pharmacie.nom_pharmacie', read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, default=None)
    attachments_count = serializers.IntegerField(source='attachments.count', read_only=True)
    messages_count = serializers.IntegerField(source='messages.count', read_only=True)

    class Meta:
        model = Ticket
        fields = (
            'id', 'reference', 'objet', 'type_intervention', 'categorie',
            'urgence', 'status', 'pharmacie', 'pharmacie_name',
            'assigned_to', 'assigned_to_name', 'created_by_name',
            'attachments_count', 'messages_count',
            'assigned_at', 'resolved_at', 'created_at', 'updated_at',
        )

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name()
        return None


class RapportEmbeddedSerializer(serializers.ModelSerializer):
    """Rapport d'intervention embarqué dans le détail ticket."""
    technicien_name = serializers.CharField(source='technicien.get_full_name', read_only=True, default=None)

    class Meta:
        from apps.interventions.models import RapportIntervention
        model = RapportIntervention
        fields = (
            'id', 'type_intervention', 'actions_realisees', 'resultat',
            'temps_passe_minutes', 'recommandations',
            'latitude', 'longitude', 'distance_pharmacie_km',
            'geolocation_datetime', 'technicien_name', 'created_at',
        )


class TicketDetailSerializer(TicketListSerializer):
    """Serializer complet avec relations imbriquées."""
    attachments = TicketAttachmentSerializer(many=True, read_only=True)
    messages = TicketMessageSerializer(many=True, read_only=True)
    status_history = TicketStatusHistorySerializer(many=True, read_only=True)
    delegations = TicketDelegationSerializer(many=True, read_only=True)
    evaluation = TicketEvaluationSerializer(read_only=True)
    rapports = RapportEmbeddedSerializer(many=True, read_only=True)
    pharmacie_region = serializers.SerializerMethodField()
    pharmacie_commune = serializers.SerializerMethodField()
    pharmacie_quartier = serializers.SerializerMethodField()
    pharmacie_zone = serializers.SerializerMethodField()
    pharmacie_adresse = serializers.CharField(source='pharmacie.adresse', read_only=True, default=None)
    pharmacie_latitude = serializers.DecimalField(source='pharmacie.latitude', max_digits=10, decimal_places=7, read_only=True, default=None)
    pharmacie_longitude = serializers.DecimalField(source='pharmacie.longitude', max_digits=10, decimal_places=7, read_only=True, default=None)
    pharmacie_tel = serializers.CharField(source='pharmacie.tel_responsable', read_only=True, default=None)
    pharmacie_email = serializers.CharField(source='pharmacie.email_pharmacie', read_only=True, default=None)
    pharmacie_responsable = serializers.CharField(source='pharmacie.nom_responsable', read_only=True, default=None)

    class Meta(TicketListSerializer.Meta):
        fields = TicketListSerializer.Meta.fields + (
            'description', 'attachments', 'messages',
            'status_history', 'delegations', 'evaluation', 'rapports',
            'pharmacie_region', 'pharmacie_commune', 'pharmacie_quartier', 'pharmacie_zone',
            'pharmacie_adresse', 'pharmacie_latitude', 'pharmacie_longitude',
            'pharmacie_tel', 'pharmacie_email', 'pharmacie_responsable',
            'started_at', 'closed_at',
            'windev_intervention_id', 'windev_besoin_id',
        )

    def get_pharmacie_region(self, obj):
        p = obj.pharmacie
        if p and p.commune and p.commune.region:
            return p.commune.region.name
        return None

    def get_pharmacie_commune(self, obj):
        p = obj.pharmacie
        if p and p.commune:
            return p.commune.name
        return None

    def get_pharmacie_quartier(self, obj):
        p = obj.pharmacie
        if p and p.quartier:
            return p.quartier.name
        return None

    def get_pharmacie_zone(self, obj):
        p = obj.pharmacie
        if not p:
            return None
        from apps.zones.models import Zone
        zone = Zone.objects.filter(
            models.Q(quartiers=p.quartier) if p.quartier_id else models.Q(),
        ).first()
        if not zone and p.commune_id:
            zone = Zone.objects.filter(communes=p.commune).first()
        if not zone and p.commune and p.commune.region_id:
            zone = Zone.objects.filter(regions=p.commune.region).first()
        return zone.name if zone else None


class TicketCreateSerializer(serializers.ModelSerializer):
    """Création d'un ticket par une pharmacie."""
    attachments = serializers.ListField(
        child=serializers.FileField(), required=False, write_only=True,
    )
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=Ticket.assigned_to.field.related_model.objects.filter(role='technicien'),
        required=False, allow_null=True,
    )

    class Meta:
        model = Ticket
        fields = (
            'id', 'reference', 'objet', 'type_intervention', 'categorie',
            'description', 'urgence', 'attachments', 'assigned_to',
        )
        read_only_fields = ('id', 'reference')

    def create(self, validated_data):
        attachments_data = validated_data.pop('attachments', [])
        manual_assignee = validated_data.pop('assigned_to', None)
        user = self.context['request'].user

        # Trouver la pharmacie liée à l'utilisateur
        try:
            pharmacie = user.pharmacie_profile
        except Exception:
            raise serializers.ValidationError(
                {'pharmacie': "Vous devez d'abord créer votre profil pharmacie."}
            )

        validated_data['pharmacie'] = pharmacie
        validated_data['created_by'] = user

        # Manual assignment
        if manual_assignee:
            from django.utils import timezone as tz
            validated_data['assigned_to'] = manual_assignee
            validated_data['assigned_at'] = tz.now()
            validated_data['status'] = 'assigne'

        ticket = Ticket.objects.create(**validated_data)

        # Sauvegarder les pièces jointes
        for file in attachments_data:
            TicketAttachment.objects.create(
                ticket=ticket,
                file=file,
                filename=file.name,
                uploaded_by=user,
            )

        # Attribution automatique seulement si pas d'assignation manuelle
        if not manual_assignee:
            from .services import auto_assign_ticket
            auto_assign_ticket(ticket)

        # Notifications
        from apps.notifications.services import notify_ticket_created
        notify_ticket_created(ticket)

        return ticket


class TicketUpdateStatusSerializer(serializers.Serializer):
    """Changement de statut d'un ticket."""
    status = serializers.ChoiceField(choices=Ticket.Status.choices)
    comment = serializers.CharField(required=False, default='')

    def validate_status(self, value):
        ticket = self.context.get('ticket')
        if not ticket:
            return value

        # Transitions autorisées
        allowed = {
            'nouveau': ['assigne'],
            'assigne': ['en_cours', 'nouveau'],
            'en_cours': ['en_attente', 'resolu'],
            'en_attente': ['en_cours'],
            'resolu': ['cloture', 'en_cours'],
            'cloture': [],
        }
        current = ticket.status
        if value not in allowed.get(current, []):
            raise serializers.ValidationError(
                f"Transition non autorisée : {current} → {value}"
            )
        return value


class DelegateTicketSerializer(serializers.Serializer):
    """Délégation d'un ticket à un autre technicien."""
    to_technicien_id = serializers.IntegerField()
    motif = serializers.CharField()

    def validate_to_technicien_id(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(pk=value, role='technicien', is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Technicien introuvable ou inactif.")
        return value
