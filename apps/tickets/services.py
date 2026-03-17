"""
Service d'attribution automatique des tickets aux techniciens.
Critères : zone de couverture, charge de travail, compétence.
"""
from django.utils import timezone
from django.db.models import Count, Q
from geopy.distance import geodesic

from apps.zones.models import TechnicienProfile


def auto_assign_ticket(ticket):
    """
    Attribue automatiquement un ticket au technicien le plus adapté.
    Retourne le technicien assigné ou None.

    Algorithme :
    1. Filtrer les techniciens disponibles et validés
    2. Filtrer par zone géographique (commune/quartier de la pharmacie)
    3. Filtrer par compétence (catégorie du ticket)
    4. Trier par charge de travail (moins de tickets actifs = prioritaire)
    5. Si GPS disponible, trier par distance
    """
    pharmacie = ticket.pharmacie

    # Base queryset : techniciens actifs, validés, disponibles
    techniciens = TechnicienProfile.objects.filter(
        user__is_active=True,
        user__is_validated=True,
        is_available=True,
    ).select_related('user').prefetch_related('zones__communes', 'zones__quartiers')

    # Filtrer par compétence
    if ticket.categorie != 'autre':
        techniciens = techniciens.filter(
            Q(competences=ticket.categorie) | Q(competences='tous')
        )

    # Filtrer par zone géographique
    zone_filtered = []
    for tech in techniciens:
        if _technicien_covers_pharmacie(tech, pharmacie):
            zone_filtered.append(tech)

    # Si aucun technicien dans la zone, prendre tous les disponibles
    candidates = zone_filtered if zone_filtered else list(techniciens)

    if not candidates:
        return None

    # Exclure les techniciens surchargés
    candidates = [t for t in candidates if not t.is_overloaded]

    if not candidates:
        # Fallback : prendre même les surchargés
        candidates = zone_filtered if zone_filtered else list(techniciens)

    # Trier par charge de travail (nombre de tickets actifs)
    candidates.sort(key=lambda t: t.active_tickets_count)

    # Si GPS disponible, départager par distance
    if pharmacie.latitude and pharmacie.longitude:
        pharma_coords = (float(pharmacie.latitude), float(pharmacie.longitude))
        min_load = candidates[0].active_tickets_count
        same_load = [t for t in candidates if t.active_tickets_count == min_load]

        if len(same_load) > 1:
            gps_candidates = []
            for t in same_load:
                if t.latitude and t.longitude:
                    tech_coords = (float(t.latitude), float(t.longitude))
                    dist = geodesic(pharma_coords, tech_coords).km
                    gps_candidates.append((t, dist))
            if gps_candidates:
                gps_candidates.sort(key=lambda x: x[1])
                return _assign(ticket, gps_candidates[0][0])

    # Assigner au technicien avec le moins de charge
    return _assign(ticket, candidates[0])


def _technicien_covers_pharmacie(technicien_profile, pharmacie):
    """Vérifie si le technicien couvre la zone de la pharmacie."""
    for zone in technicien_profile.zones.all():
        # Vérifier par quartier
        if pharmacie.quartier_id:
            if zone.quartiers.filter(id=pharmacie.quartier_id).exists():
                return True
        # Vérifier par commune
        if pharmacie.commune_id:
            if zone.communes.filter(id=pharmacie.commune_id).exists():
                return True
            # Vérifier par région de la commune
            if pharmacie.commune and pharmacie.commune.region_id:
                if zone.regions.filter(id=pharmacie.commune.region_id).exists():
                    return True
    return False


def _assign(ticket, technicien_profile):
    """Effectue l'assignation du ticket."""
    ticket.assigned_to = technicien_profile.user
    ticket.assigned_at = timezone.now()
    ticket.status = 'assigne'
    ticket.save(update_fields=['assigned_to', 'assigned_at', 'status', 'updated_at'])
    return technicien_profile.user
