import logging
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view

from .serializers import (
    UserSerializer, UserCreateSerializer, RegisterSerializer,
    ChangePasswordSerializer, ProfileSerializer,
)
from .permissions import IsAdmin, IsAdminOrSelf

User = get_user_model()


@extend_schema(tags=['Auth'])
class RegisterView(generics.CreateAPIView):
    """Inscription d'une pharmacie (nécessite validation admin)."""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


@extend_schema(tags=['Auth'])
class LoginView(TokenObtainPairView):
    """Connexion - retourne access + refresh token + user info.
    Accepte username OU email dans le champ 'username'.
    """

    def post(self, request, *args, **kwargs):
        # Allow login by email: resolve email → username
        login_field = request.data.get('username', '')
        resolved_user = None
        if '@' in login_field:
            try:
                resolved_user = User.objects.get(email__iexact=login_field)
                # Replace email with actual username in request data
                if hasattr(request.data, '_mutable'):
                    request.data._mutable = True
                    request.data['username'] = resolved_user.username
                    request.data._mutable = False
                else:
                    request.data['username'] = resolved_user.username
            except User.DoesNotExist:
                pass

        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            if resolved_user is None:
                resolved_user = User.objects.get(username=request.data.get('username'))
            user_data = {
                'id': resolved_user.id,
                'username': resolved_user.username,
                'email': resolved_user.email,
                'first_name': resolved_user.first_name,
                'last_name': resolved_user.last_name,
                'role': resolved_user.role,
                'phone': resolved_user.phone,
                'is_validated': resolved_user.is_validated,
            }
            # Add pharmacie_id for pharmacie users
            if resolved_user.role == 'pharmacie':
                try:
                    user_data['pharmacie_id'] = resolved_user.pharmacie_profile.id
                except Exception:
                    user_data['pharmacie_id'] = None
            response.data['user'] = user_data
        return response


@extend_schema(tags=['Auth'])
class RefreshTokenView(TokenRefreshView):
    """Rafraîchir le token d'accès."""
    pass


@extend_schema(tags=['Auth'])
class LogoutView(generics.GenericAPIView):
    """Déconnexion - blacklist le refresh token."""
    permission_classes = [IsAuthenticated]

    @extend_schema(request={'application/json': {'type': 'object', 'properties': {'refresh': {'type': 'string'}}}})
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Déconnexion réussie.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'Token invalide.'}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Auth'])
class ProfileView(generics.RetrieveUpdateAPIView):
    """Voir / modifier son profil."""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(tags=['Auth'])
class ChangePasswordView(generics.UpdateAPIView):
    """Changer son mot de passe."""
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Mot de passe modifié avec succès.'})


@extend_schema_view(
    list=extend_schema(tags=['Auth']),
    retrieve=extend_schema(tags=['Auth']),
    create=extend_schema(tags=['Auth']),
    update=extend_schema(tags=['Auth']),
    partial_update=extend_schema(tags=['Auth']),
    destroy=extend_schema(tags=['Auth']),
)
class UserViewSet(viewsets.ModelViewSet):
    """CRUD utilisateurs (admin uniquement)."""
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['role', 'is_validated', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['created_at', 'username', 'role']

    def get_queryset(self):
        qs = super().get_queryset()
        pharmacie_id = self.request.query_params.get('pharmacie')
        if pharmacie_id:
            from apps.pharmacies.models import Pharmacie
            from apps.zones.models import Zone, TechnicienProfile
            from django.db.models import Q
            try:
                pharma = Pharmacie.objects.select_related('commune').get(pk=pharmacie_id)
            except Pharmacie.DoesNotExist:
                return qs.none()
            # Find zones covering this pharmacy
            zone_q = Q()
            if pharma.quartier_id:
                zone_q |= Q(quartiers__id=pharma.quartier_id)
            if pharma.commune_id:
                zone_q |= Q(communes__id=pharma.commune_id)
            if pharma.commune and pharma.commune.region_id:
                zone_q |= Q(regions__id=pharma.commune.region_id)
            # Pharmacy owner user + techniciens in matching zones
            user_ids = {pharma.user_id}
            if zone_q:
                matching_zone_ids = Zone.objects.filter(zone_q).values_list('id', flat=True)
                tech_user_ids = TechnicienProfile.objects.filter(
                    zones__id__in=matching_zone_ids
                ).values_list('user_id', flat=True).distinct()
                user_ids.update(tech_user_ids)
            qs = qs.filter(id__in=user_ids)
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @extend_schema(tags=['Auth'])
    @action(detail=True, methods=['post'])
    def validate_account(self, request, pk=None):
        """Valider le compte d'un utilisateur."""
        user = self.get_object()
        user.is_validated = True
        user.save(update_fields=['is_validated'])
        return Response({'detail': f'Compte de {user.username} validé.'})

    @extend_schema(tags=['Auth'])
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Désactiver un utilisateur."""
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=['is_active'])
        return Response({'detail': f'Compte de {user.username} désactivé.'})

    @extend_schema(tags=['Auth'])
    @action(detail=True, methods=['post'], url_path='set_password')
    def set_password(self, request, pk=None):
        """Admin: forcer le mot de passe d'un utilisateur."""
        logger = logging.getLogger('accounts')
        user = self.get_object()
        new_password = request.data.get('new_password')
        logger.warning(f"[set_password] user={user.username} pk={pk} password_len={len(new_password) if new_password else 0}")
        if not new_password:
            return Response(
                {'detail': 'Le champ new_password est requis.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()
        # Vérification immédiate
        user.refresh_from_db()
        ok = user.check_password(new_password)
        logger.warning(f"[set_password] user={user.username} check_after_save={ok}")
        return Response({'detail': f'Mot de passe de {user.username} modifié avec succès (vérifié: {ok}).'})
