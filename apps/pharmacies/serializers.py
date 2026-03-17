from rest_framework import serializers
from .models import Pharmacie, ContactPharmacie, EquipementPharmacie
from apps.accounts.serializers import UserSerializer


class ContactPharmacieSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactPharmacie
        fields = ('id', 'nom', 'fonction', 'telephone', 'email')


class EquipementPharmacieSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipementPharmacie
        fields = (
            'id', 'nom', 'type_equipement', 'numero_serie',
            'date_installation', 'description', 'is_active', 'created_at',
        )


class PharmacieSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    commune_name = serializers.CharField(source='commune.name', read_only=True, default=None)
    quartier_name = serializers.CharField(source='quartier.name', read_only=True, default=None)
    tickets_count = serializers.SerializerMethodField()

    class Meta:
        model = Pharmacie
        fields = (
            'id', 'user', 'nom_pharmacie', 'code_2st', 'adresse', 'ville',
            'commune', 'commune_name', 'quartier', 'quartier_name',
            'latitude', 'longitude', 'nom_responsable', 'tel_responsable',
            'email_pharmacie', 'logo', 'sous_contrat', 'date_contrat',
            'notes', 'windev_client_id', 'tickets_count',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_tickets_count(self, obj):
        return obj.tickets.count() if hasattr(obj, 'tickets') else 0


class PharmacieDetailSerializer(PharmacieSerializer):
    contacts = ContactPharmacieSerializer(many=True, read_only=True)
    equipements = EquipementPharmacieSerializer(many=True, read_only=True)

    class Meta(PharmacieSerializer.Meta):
        fields = PharmacieSerializer.Meta.fields + ('contacts', 'equipements')


class PharmacieCreateSerializer(serializers.ModelSerializer):
    """Pour la création du profil pharmacie par l'utilisateur connecté."""
    class Meta:
        model = Pharmacie
        fields = (
            'id', 'nom_pharmacie', 'code_2st', 'adresse', 'ville',
            'commune', 'quartier', 'latitude', 'longitude',
            'nom_responsable', 'tel_responsable', 'email_pharmacie', 'logo',
        )

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
