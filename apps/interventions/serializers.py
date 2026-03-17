from rest_framework import serializers
from django.utils import timezone
from geopy.distance import geodesic

from .models import RapportIntervention, PhotoIntervention


class PhotoInterventionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoIntervention
        fields = ('id', 'image', 'description', 'created_at')
        read_only_fields = ('id', 'created_at')


class RapportInterventionListSerializer(serializers.ModelSerializer):
    technicien_name = serializers.CharField(source='technicien.get_full_name', read_only=True, default=None)
    ticket_reference = serializers.CharField(source='ticket.reference', read_only=True)
    photos_count = serializers.IntegerField(source='photos.count', read_only=True)

    class Meta:
        model = RapportIntervention
        fields = (
            'id', 'ticket', 'ticket_reference', 'technicien', 'technicien_name',
            'type_intervention', 'resultat', 'temps_passe_minutes',
            'distance_pharmacie_km', 'photos_count', 'created_at',
        )


class RapportInterventionDetailSerializer(RapportInterventionListSerializer):
    photos = PhotoInterventionSerializer(many=True, read_only=True)

    class Meta(RapportInterventionListSerializer.Meta):
        fields = RapportInterventionListSerializer.Meta.fields + (
            'actions_realisees', 'recommandations', 'signature_numerique',
            'latitude', 'longitude', 'geolocation_datetime',
            'photos', 'updated_at',
        )


class RapportInterventionCreateSerializer(serializers.ModelSerializer):
    """
    Création d'un rapport d'intervention.
    Pour les interventions sur site, latitude et longitude sont obligatoires.
    """
    photos = serializers.ListField(
        child=serializers.ImageField(), required=False, write_only=True,
    )

    class Meta:
        model = RapportIntervention
        fields = (
            'id', 'ticket', 'type_intervention', 'actions_realisees',
            'resultat', 'temps_passe_minutes', 'recommandations',
            'signature_numerique', 'latitude', 'longitude', 'photos',
        )
        read_only_fields = ('id',)

    def validate(self, attrs):
        # Pour les interventions sur site, la géolocalisation est obligatoire
        if attrs.get('type_intervention') == 'sur_site':
            if not attrs.get('latitude') or not attrs.get('longitude'):
                raise serializers.ValidationError({
                    'latitude': "La géolocalisation est obligatoire pour une intervention sur site.",
                    'longitude': "La géolocalisation est obligatoire pour une intervention sur site.",
                })
        return attrs

    def create(self, validated_data):
        photos_data = validated_data.pop('photos', [])
        user = self.context['request'].user
        validated_data['technicien'] = user

        # Calculer la distance pharmacie ↔ technicien si GPS disponible
        ticket = validated_data['ticket']
        pharmacie = ticket.pharmacie
        if (validated_data.get('latitude') and validated_data.get('longitude')
                and pharmacie.latitude and pharmacie.longitude):
            tech_coords = (float(validated_data['latitude']), float(validated_data['longitude']))
            pharma_coords = (float(pharmacie.latitude), float(pharmacie.longitude))
            distance = geodesic(tech_coords, pharma_coords).km
            validated_data['distance_pharmacie_km'] = round(distance, 2)

        if validated_data.get('latitude'):
            validated_data['geolocation_datetime'] = timezone.now()

        rapport = RapportIntervention.objects.create(**validated_data)

        # Sauvegarder les photos
        for photo in photos_data:
            PhotoIntervention.objects.create(rapport=rapport, image=photo)

        return rapport
