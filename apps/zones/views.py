from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Region, Commune, Quartier, Zone, TechnicienProfile
from .serializers import (
    RegionSerializer, CommuneSerializer, QuartierSerializer,
    ZoneSerializer, ZoneDetailSerializer,
    TechnicienProfileSerializer, TechnicienLocationSerializer,
)
from apps.accounts.permissions import IsAdmin, IsAdminOrTechnicien


@extend_schema_view(
    list=extend_schema(tags=['Zones']),
    retrieve=extend_schema(tags=['Zones']),
    create=extend_schema(tags=['Zones']),
    update=extend_schema(tags=['Zones']),
    partial_update=extend_schema(tags=['Zones']),
    destroy=extend_schema(tags=['Zones']),
)
class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]


@extend_schema_view(
    list=extend_schema(tags=['Zones']),
    retrieve=extend_schema(tags=['Zones']),
    create=extend_schema(tags=['Zones']),
    update=extend_schema(tags=['Zones']),
    partial_update=extend_schema(tags=['Zones']),
    destroy=extend_schema(tags=['Zones']),
)
class CommuneViewSet(viewsets.ModelViewSet):
    queryset = Commune.objects.select_related('region').all()
    serializer_class = CommuneSerializer
    filterset_fields = ['region', 'is_active']
    search_fields = ['name', 'code']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]


@extend_schema_view(
    list=extend_schema(tags=['Zones']),
    retrieve=extend_schema(tags=['Zones']),
    create=extend_schema(tags=['Zones']),
    update=extend_schema(tags=['Zones']),
    partial_update=extend_schema(tags=['Zones']),
    destroy=extend_schema(tags=['Zones']),
)
class QuartierViewSet(viewsets.ModelViewSet):
    queryset = Quartier.objects.select_related('commune', 'commune__region').all()
    serializer_class = QuartierSerializer
    filterset_fields = ['commune', 'commune__region', 'is_active']
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]


@extend_schema_view(
    list=extend_schema(tags=['Zones']),
    retrieve=extend_schema(tags=['Zones']),
    create=extend_schema(tags=['Zones']),
    update=extend_schema(tags=['Zones']),
    partial_update=extend_schema(tags=['Zones']),
    destroy=extend_schema(tags=['Zones']),
)
class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.prefetch_related(
        'regions', 'communes', 'quartiers', 'techniciens', 'techniciens__user',
    ).all()
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ZoneDetailSerializer
        return ZoneSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]


@extend_schema_view(
    list=extend_schema(tags=['Techniciens']),
    retrieve=extend_schema(tags=['Techniciens']),
    create=extend_schema(tags=['Techniciens']),
    update=extend_schema(tags=['Techniciens']),
    partial_update=extend_schema(tags=['Techniciens']),
    destroy=extend_schema(tags=['Techniciens']),
)
class TechnicienProfileViewSet(viewsets.ModelViewSet):
    queryset = TechnicienProfile.objects.select_related('user').prefetch_related('zones').all()
    serializer_class = TechnicienProfileSerializer
    filterset_fields = ['is_available', 'competences', 'zones']
    search_fields = ['user__first_name', 'user__last_name', 'user__username']

    def get_queryset(self):
        qs = super().get_queryset()
        pharmacie_id = self.request.query_params.get('pharmacie')
        if pharmacie_id:
            from apps.pharmacies.models import Pharmacie
            try:
                pharma = Pharmacie.objects.select_related('commune').get(pk=pharmacie_id)
            except Pharmacie.DoesNotExist:
                return qs.none()
            from django.db.models import Q
            zone_q = Q()
            if pharma.quartier_id:
                zone_q |= Q(quartiers__id=pharma.quartier_id)
            if pharma.commune_id:
                zone_q |= Q(communes__id=pharma.commune_id)
            if pharma.commune and pharma.commune.region_id:
                zone_q |= Q(regions__id=pharma.commune.region_id)
            if zone_q:
                matching_zone_ids = Zone.objects.filter(zone_q).values_list('id', flat=True)
                qs = qs.filter(zones__id__in=matching_zone_ids).distinct()
            else:
                return qs.none()
        return qs

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        if self.action in ['update_location', 'toggle_availability']:
            return [IsAuthenticated(), IsAdminOrTechnicien()]
        return [IsAuthenticated(), IsAdmin()]

    @extend_schema(tags=['Techniciens'], request=TechnicienLocationSerializer)
    @action(detail=False, methods=['post'])
    def update_location(self, request):
        """Mettre à jour la géolocalisation du technicien connecté."""
        try:
            profile = request.user.technicien_profile
        except TechnicienProfile.DoesNotExist:
            return Response(
                {'detail': 'Profil technicien introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TechnicienLocationSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(last_location_update=timezone.now())
        return Response(serializer.data)

    @extend_schema(tags=['Techniciens'])
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Liste des techniciens disponibles."""
        qs = self.get_queryset().filter(is_available=True, user__is_active=True, user__is_validated=True)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(tags=['Techniciens'])
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsAdminOrTechnicien])
    def toggle_availability(self, request):
        """Permet au technicien de basculer sa disponibilité."""
        try:
            profile = request.user.technicien_profile
        except TechnicienProfile.DoesNotExist:
            return Response(
                {'detail': 'Profil technicien introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        profile.is_available = not profile.is_available
        profile.save(update_fields=['is_available'])
        return Response({
            'is_available': profile.is_available,
            'detail': 'Disponibilité mise à jour.',
        })

    @extend_schema(tags=['Techniciens'])
    @action(detail=False, methods=['get'])
    def for_pharmacie(self, request):
        """Liste des techniciens couvrant la zone de la pharmacie de l'utilisateur connecté."""
        try:
            pharmacie = request.user.pharmacie_profile
        except Exception:
            return Response(
                {'detail': 'Profil pharmacie introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Get all active techniciens
        all_techs = self.get_queryset().filter(
            user__is_active=True, user__is_validated=True,
        )
        # Filter by zone match
        zone_techs = []
        other_techs = []
        for tech in all_techs:
            matches = False
            for zone in tech.zones.all():
                if pharmacie.quartier_id and zone.quartiers.filter(id=pharmacie.quartier_id).exists():
                    matches = True; break
                if pharmacie.commune_id and zone.communes.filter(id=pharmacie.commune_id).exists():
                    matches = True; break
                if pharmacie.commune and pharmacie.commune.region_id and zone.regions.filter(id=pharmacie.commune.region_id).exists():
                    matches = True; break
            if matches:
                zone_techs.append(tech)
            else:
                other_techs.append(tech)
        serializer = self.get_serializer(zone_techs + other_techs, many=True)
        data = serializer.data
        # Mark which ones are in zone
        zone_ids = {t.id for t in zone_techs}
        for item in data:
            item['in_zone'] = item['id'] in zone_ids
        return Response(data)
