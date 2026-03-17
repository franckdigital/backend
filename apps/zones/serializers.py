from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Region, Commune, Quartier, Zone, TechnicienProfile
from apps.accounts.serializers import UserSerializer

User = get_user_model()


class RegionSerializer(serializers.ModelSerializer):
    communes_count = serializers.IntegerField(source='communes.count', read_only=True)

    class Meta:
        model = Region
        fields = ('id', 'name', 'code', 'is_active', 'communes_count', 'created_at')


class CommuneSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    quartiers_count = serializers.IntegerField(source='quartiers.count', read_only=True)

    class Meta:
        model = Commune
        fields = ('id', 'name', 'code', 'region', 'region_name', 'is_active', 'quartiers_count', 'created_at')


class QuartierSerializer(serializers.ModelSerializer):
    commune_name = serializers.CharField(source='commune.name', read_only=True)
    region_name = serializers.CharField(source='commune.region.name', read_only=True)

    class Meta:
        model = Quartier
        fields = ('id', 'name', 'commune', 'commune_name', 'region_name', 'is_active', 'created_at')


class ZoneSerializer(serializers.ModelSerializer):
    techniciens_count = serializers.IntegerField(source='techniciens.count', read_only=True)

    class Meta:
        model = Zone
        fields = (
            'id', 'name', 'description', 'regions', 'communes', 'quartiers',
            'is_active', 'techniciens_count', 'created_at', 'updated_at',
        )


class TechnicienProfileListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    active_tickets_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = TechnicienProfile
        fields = ('id', 'user', 'competences', 'is_available', 'active_tickets_count')


class ZoneDetailSerializer(ZoneSerializer):
    regions = RegionSerializer(many=True, read_only=True)
    communes = CommuneSerializer(many=True, read_only=True)
    quartiers = QuartierSerializer(many=True, read_only=True)
    techniciens = TechnicienProfileListSerializer(many=True, read_only=True)


class TechnicienProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True, source='user', required=False,
    )
    zones = ZoneSerializer(many=True, read_only=True)
    zone_ids = serializers.PrimaryKeyRelatedField(
        queryset=Zone.objects.all(), many=True, write_only=True, source='zones', required=False,
    )
    active_tickets_count = serializers.IntegerField(read_only=True)
    is_overloaded = serializers.BooleanField(read_only=True)

    class Meta:
        model = TechnicienProfile
        fields = (
            'id', 'user', 'user_id', 'zones', 'zone_ids', 'competences',
            'max_tickets_simultanes', 'is_available',
            'latitude', 'longitude', 'last_location_update',
            'active_tickets_count', 'is_overloaded',
        )


class TechnicienLocationSerializer(serializers.ModelSerializer):
    """Pour la mise à jour de la géolocalisation du technicien."""
    class Meta:
        model = TechnicienProfile
        fields = ('latitude', 'longitude')
