from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import RapportIntervention, PhotoIntervention
from .serializers import (
    RapportInterventionListSerializer,
    RapportInterventionDetailSerializer,
    RapportInterventionCreateSerializer,
    PhotoInterventionSerializer,
)
from apps.accounts.permissions import IsAdminOrTechnicien


@extend_schema_view(
    list=extend_schema(tags=['Interventions']),
    retrieve=extend_schema(tags=['Interventions']),
    create=extend_schema(tags=['Interventions']),
    update=extend_schema(tags=['Interventions']),
    partial_update=extend_schema(tags=['Interventions']),
    destroy=extend_schema(tags=['Interventions']),
)
class RapportInterventionViewSet(viewsets.ModelViewSet):
    filterset_fields = ['ticket', 'technicien', 'type_intervention', 'resultat']
    search_fields = ['actions_realisees', 'recommandations', 'ticket__reference']
    ordering_fields = ['created_at', 'temps_passe_minutes']

    def get_queryset(self):
        user = self.request.user
        qs = RapportIntervention.objects.select_related(
            'ticket', 'technicien'
        ).prefetch_related('photos')

        if user.is_technicien:
            qs = qs.filter(technicien=user)
        elif user.is_pharmacie:
            qs = qs.filter(ticket__pharmacie__user=user)
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RapportInterventionDetailSerializer
        if self.action == 'create':
            return RapportInterventionCreateSerializer
        return RapportInterventionListSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsAdminOrTechnicien()]
        return [IsAuthenticated()]


@extend_schema_view(
    list=extend_schema(tags=['Interventions']),
    create=extend_schema(tags=['Interventions']),
)
class PhotoInterventionViewSet(viewsets.ModelViewSet):
    serializer_class = PhotoInterventionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return PhotoIntervention.objects.filter(rapport_id=self.kwargs['rapport_pk'])

    def perform_create(self, serializer):
        serializer.save(rapport_id=self.kwargs['rapport_pk'])
