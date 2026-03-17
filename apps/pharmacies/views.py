from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Pharmacie, ContactPharmacie, EquipementPharmacie
from .serializers import (
    PharmacieSerializer, PharmacieDetailSerializer, PharmacieCreateSerializer,
    ContactPharmacieSerializer, EquipementPharmacieSerializer,
)
from apps.accounts.permissions import IsAdmin, IsAdminOrPharmacie


@extend_schema_view(
    list=extend_schema(tags=['Pharmacies']),
    retrieve=extend_schema(tags=['Pharmacies']),
    create=extend_schema(tags=['Pharmacies']),
    update=extend_schema(tags=['Pharmacies']),
    partial_update=extend_schema(tags=['Pharmacies']),
    destroy=extend_schema(tags=['Pharmacies']),
)
class PharmacieViewSet(viewsets.ModelViewSet):
    filterset_fields = ['sous_contrat', 'commune', 'quartier', 'ville']
    search_fields = ['nom_pharmacie', 'code_2st', 'nom_responsable', 'adresse']
    ordering_fields = ['nom_pharmacie', 'created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Pharmacie.objects.select_related('user', 'commune', 'commune__region', 'quartier').all()
        if user.is_pharmacie:
            qs = qs.filter(user=user)
        # Technician: only pharmacies in their zones (by commune or quartier)
        elif user.is_technicien:
            profile = getattr(user, 'technicien_profile', None)
            if profile:
                zone_ids = profile.zones.values_list('id', flat=True)
                from django.db.models import Q
                qs = qs.filter(
                    Q(commune__zones__id__in=zone_ids) |
                    Q(quartier__zones__id__in=zone_ids)
                ).distinct()
            else:
                qs = qs.none()
        # Filter by specific pharmacy
        pharmacie_id = self.request.query_params.get('pharmacie')
        if pharmacie_id:
            qs = qs.filter(pk=pharmacie_id)
        # Filter by zone (pharmacies whose commune is in that zone)
        zone = self.request.query_params.get('zone')
        if zone:
            qs = qs.filter(commune__zones__id=zone)
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PharmacieDetailSerializer
        if self.action == 'create':
            return PharmacieCreateSerializer
        return PharmacieSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsAdminOrPharmacie()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    @extend_schema(tags=['Pharmacies'])
    @action(detail=False, methods=['get', 'patch'])
    def my_pharmacie(self, request):
        """Récupérer ou mettre à jour le profil pharmacie de l'utilisateur connecté."""
        if request.method == 'PATCH':
            try:
                pharmacie = Pharmacie.objects.get(user=request.user)
                serializer = PharmacieCreateSerializer(pharmacie, data=request.data, partial=True, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                pharmacie.refresh_from_db()
                return Response(PharmacieDetailSerializer(pharmacie).data)
            except Pharmacie.DoesNotExist:
                # Create a new pharmacie profile for the user
                data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
                serializer = PharmacieCreateSerializer(data=data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                pharmacie = serializer.save()
                return Response(PharmacieDetailSerializer(pharmacie).data, status=status.HTTP_201_CREATED)
        try:
            pharmacie = Pharmacie.objects.get(user=request.user)
            serializer = PharmacieDetailSerializer(pharmacie)
            return Response(serializer.data)
        except Pharmacie.DoesNotExist:
            return Response(
                {'detail': 'Profil pharmacie introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )


@extend_schema_view(
    list=extend_schema(tags=['Pharmacies']),
    retrieve=extend_schema(tags=['Pharmacies']),
    create=extend_schema(tags=['Pharmacies']),
    update=extend_schema(tags=['Pharmacies']),
    partial_update=extend_schema(tags=['Pharmacies']),
    destroy=extend_schema(tags=['Pharmacies']),
)
class ContactPharmacieViewSet(viewsets.ModelViewSet):
    serializer_class = ContactPharmacieSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ContactPharmacie.objects.filter(pharmacie_id=self.kwargs['pharmacie_pk'])

    def perform_create(self, serializer):
        serializer.save(pharmacie_id=self.kwargs['pharmacie_pk'])


@extend_schema_view(
    list=extend_schema(tags=['Pharmacies']),
    retrieve=extend_schema(tags=['Pharmacies']),
    create=extend_schema(tags=['Pharmacies']),
    update=extend_schema(tags=['Pharmacies']),
    partial_update=extend_schema(tags=['Pharmacies']),
    destroy=extend_schema(tags=['Pharmacies']),
)
class EquipementPharmacieViewSet(viewsets.ModelViewSet):
    serializer_class = EquipementPharmacieSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EquipementPharmacie.objects.filter(pharmacie_id=self.kwargs['pharmacie_pk'])

    def perform_create(self, serializer):
        serializer.save(pharmacie_id=self.kwargs['pharmacie_pk'])
