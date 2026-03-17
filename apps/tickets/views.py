from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import (
    Ticket, TicketAttachment, TicketMessage,
    TicketStatusHistory, TicketDelegation, TicketEvaluation,
)
from .serializers import (
    TicketListSerializer, TicketDetailSerializer, TicketCreateSerializer,
    TicketUpdateStatusSerializer, DelegateTicketSerializer,
    TicketMessageSerializer, TicketAttachmentSerializer,
    TicketEvaluationSerializer,
)
from apps.accounts.permissions import IsAdmin, IsPharmacie, IsTechnicien
from apps.notifications.services import (
    notify_ticket_created, notify_ticket_status_changed,
    notify_new_message,
)

User = get_user_model()


@extend_schema_view(
    list=extend_schema(tags=['Tickets']),
    retrieve=extend_schema(tags=['Tickets']),
    create=extend_schema(tags=['Tickets']),
    update=extend_schema(tags=['Tickets']),
    partial_update=extend_schema(tags=['Tickets']),
    destroy=extend_schema(tags=['Tickets']),
)
class TicketViewSet(viewsets.ModelViewSet):
    filterset_fields = ['status', 'urgence', 'categorie', 'type_intervention', 'assigned_to', 'pharmacie']
    search_fields = ['reference', 'objet', 'description']
    ordering_fields = ['created_at', 'urgence', 'status', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        qs = Ticket.objects.select_related(
            'pharmacie', 'pharmacie__commune', 'pharmacie__commune__region',
            'pharmacie__quartier', 'created_by', 'assigned_to',
        ).prefetch_related('attachments', 'messages', 'status_history', 'rapports')

        if user.is_pharmacie:
            # La pharmacie ne voit que ses propres tickets
            qs = qs.filter(pharmacie__user=user)
        elif user.is_technicien:
            # Le technicien voit ses tickets assignés
            qs = qs.filter(assigned_to=user)
        # Admin voit tout
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TicketDetailSerializer
        if self.action == 'create':
            return TicketCreateSerializer
        return TicketListSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsPharmacie()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    @extend_schema(tags=['Tickets'], request=TicketUpdateStatusSerializer)
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Changer le statut d'un ticket."""
        ticket = self.get_object()
        serializer = TicketUpdateStatusSerializer(
            data=request.data,
            context={'ticket': ticket, 'request': request},
        )
        serializer.is_valid(raise_exception=True)

        old_status = ticket.status
        new_status = serializer.validated_data['status']

        ticket.status = new_status
        update_fields = ['status', 'updated_at']

        if new_status == 'en_cours' and not ticket.started_at:
            ticket.started_at = timezone.now()
            update_fields.append('started_at')
        elif new_status == 'resolu':
            ticket.resolved_at = timezone.now()
            update_fields.append('resolved_at')
        elif new_status == 'cloture':
            ticket.closed_at = timezone.now()
            update_fields.append('closed_at')

        ticket.save(update_fields=update_fields)

        TicketStatusHistory.objects.create(
            ticket=ticket,
            old_status=old_status,
            new_status=new_status,
            changed_by=request.user,
            comment=serializer.validated_data.get('comment', ''),
        )

        notify_ticket_status_changed(ticket, old_status, new_status, request.user)

        return Response(TicketDetailSerializer(ticket).data)

    @extend_schema(tags=['Tickets'])
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Technicien accepte un ticket assigné."""
        ticket = self.get_object()
        if ticket.assigned_to != request.user:
            return Response(
                {'detail': "Ce ticket ne vous est pas assigné."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if ticket.status != 'assigne':
            return Response(
                {'detail': "Le ticket doit être au statut 'Assigné'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        old_status = ticket.status
        ticket.status = 'en_cours'
        ticket.started_at = timezone.now()
        ticket.save(update_fields=['status', 'started_at', 'updated_at'])

        TicketStatusHistory.objects.create(
            ticket=ticket, old_status=old_status, new_status='en_cours',
            changed_by=request.user, comment='Ticket accepté par le technicien',
        )

        notify_ticket_status_changed(ticket, old_status, 'en_cours', request.user)

        return Response(TicketDetailSerializer(ticket).data)

    @extend_schema(tags=['Tickets'], request=DelegateTicketSerializer)
    @action(detail=True, methods=['post'])
    def delegate(self, request, pk=None):
        """Technicien délègue un ticket à un autre technicien."""
        ticket = self.get_object()
        if ticket.assigned_to != request.user:
            return Response(
                {'detail': "Ce ticket ne vous est pas assigné."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = DelegateTicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        to_user = User.objects.get(pk=serializer.validated_data['to_technicien_id'])

        TicketDelegation.objects.create(
            ticket=ticket,
            from_technicien=request.user,
            to_technicien=to_user,
            motif=serializer.validated_data['motif'],
        )

        ticket.assigned_to = to_user
        ticket.assigned_at = timezone.now()
        ticket.status = 'assigne'
        ticket.save(update_fields=['assigned_to', 'assigned_at', 'status', 'updated_at'])

        TicketStatusHistory.objects.create(
            ticket=ticket, old_status='assigne', new_status='assigne',
            changed_by=request.user,
            comment=f"Délégué à {to_user.get_full_name()}. Motif: {serializer.validated_data['motif']}",
        )

        # Notify new assignee
        from apps.notifications.services import notify
        notify(
            to_user, 'ticket_delegated',
            f"Ticket {ticket.reference} délégué",
            f"Le ticket {ticket.reference} vous a été délégué par {request.user.get_full_name()}.",
            ticket=ticket,
        )

        return Response(TicketDetailSerializer(ticket).data)

    @extend_schema(tags=['Tickets'], request=TicketEvaluationSerializer)
    @action(detail=True, methods=['post'])
    def evaluate(self, request, pk=None):
        """Pharmacie évalue le service après résolution."""
        ticket = self.get_object()
        if ticket.status not in ('resolu', 'cloture'):
            return Response(
                {'detail': "Le ticket doit être résolu ou clôturé."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if hasattr(ticket, 'evaluation') and ticket.evaluation:
            return Response(
                {'detail': "Ce ticket a déjà été évalué."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TicketEvaluationSerializer(
            data={**request.data, 'ticket': ticket.id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=['Tickets'])
    @action(detail=True, methods=['post'])
    def reassign(self, request, pk=None):
        """Admin réassigne manuellement un ticket."""
        if not request.user.is_admin:
            return Response(
                {'detail': "Réservé aux administrateurs."},
                status=status.HTTP_403_FORBIDDEN,
            )
        ticket = self.get_object()
        technicien_id = request.data.get('technicien_id')
        if not technicien_id:
            return Response(
                {'detail': "technicien_id requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            tech = User.objects.get(pk=technicien_id, role='technicien', is_active=True)
        except User.DoesNotExist:
            return Response(
                {'detail': "Technicien introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        old_assigned = ticket.assigned_to
        ticket.assigned_to = tech
        ticket.assigned_at = timezone.now()
        if ticket.status == 'nouveau':
            ticket.status = 'assigne'
        ticket.save(update_fields=['assigned_to', 'assigned_at', 'status', 'updated_at'])

        TicketStatusHistory.objects.create(
            ticket=ticket,
            old_status=ticket.status,
            new_status=ticket.status,
            changed_by=request.user,
            comment=f"Réassigné de {old_assigned} à {tech.get_full_name()} par l'admin",
        )

        # Notify new assignee
        from apps.notifications.services import notify
        notify(
            tech, 'ticket_assigned',
            f"Ticket {ticket.reference} assigné",
            f"Le ticket {ticket.reference} vous a été assigné par l'admin.",
            ticket=ticket,
        )

        return Response(TicketDetailSerializer(ticket).data)


@extend_schema_view(
    list=extend_schema(tags=['Tickets']),
    create=extend_schema(tags=['Tickets']),
)
class TicketMessageViewSet(viewsets.ModelViewSet):
    """Messages dans un ticket."""
    serializer_class = TicketMessageSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        qs = TicketMessage.objects.filter(
            ticket_id=self.kwargs['ticket_pk']
        ).select_related('sender')
        # Les pharmacies ne voient pas les notes internes
        if self.request.user.is_pharmacie:
            qs = qs.filter(is_internal=False)
        return qs

    def perform_create(self, serializer):
        msg = serializer.save(
            ticket_id=self.kwargs['ticket_pk'],
            sender=self.request.user,
        )
        notify_new_message(msg)


@extend_schema_view(
    list=extend_schema(tags=['Tickets']),
    create=extend_schema(tags=['Tickets']),
)
class TicketAttachmentViewSet(viewsets.ModelViewSet):
    """Pièces jointes d'un ticket."""
    serializer_class = TicketAttachmentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return TicketAttachment.objects.filter(ticket_id=self.kwargs['ticket_pk'])

    def perform_create(self, serializer):
        serializer.save(
            ticket_id=self.kwargs['ticket_pk'],
            uploaded_by=self.request.user,
        )
