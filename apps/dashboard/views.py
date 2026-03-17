from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Avg, Q, F
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema

from apps.tickets.models import Ticket, TicketEvaluation
from apps.interventions.models import RapportIntervention
from apps.pharmacies.models import Pharmacie
from apps.zones.models import TechnicienProfile, Zone
from apps.accounts.permissions import IsAdmin


class DashboardStatsView(APIView):
    """Tableau de bord principal (admin)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(tags=['Dashboard'])
    def get(self, request):
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # Optional pharmacy filter
        pharmacy_id = request.query_params.get('pharmacy_id')
        base_qs = Ticket.objects.all()
        if pharmacy_id:
            base_qs = base_qs.filter(pharmacie_id=pharmacy_id)

        # Tickets par statut
        tickets_by_status = dict(
            base_qs.values_list('status').annotate(count=Count('id')).values_list('status', 'count')
        )

        # Tickets par urgence
        tickets_by_urgence = dict(
            base_qs.values_list('urgence').annotate(count=Count('id')).values_list('urgence', 'count')
        )

        # Tickets créés ce mois
        tickets_this_month = base_qs.filter(created_at__gte=thirty_days_ago).count()

        # Temps moyen de résolution (en heures)
        resolved_tickets = base_qs.filter(
            resolved_at__isnull=False, created_at__isnull=False
        ).exclude(resolved_at=None)
        avg_resolution = None
        if resolved_tickets.exists():
            durations = []
            for t in resolved_tickets[:500]:
                delta = (t.resolved_at - t.created_at).total_seconds() / 3600
                durations.append(delta)
            if durations:
                avg_resolution = round(sum(durations) / len(durations), 1)

        # Note moyenne des évaluations
        eval_qs = TicketEvaluation.objects.all()
        if pharmacy_id:
            eval_qs = eval_qs.filter(ticket__pharmacie_id=pharmacy_id)
        avg_rating = eval_qs.aggregate(avg=Avg('note'))['avg']

        # Performance techniciens (top 10)
        techniciens_perf = []
        for profile in TechnicienProfile.objects.select_related('user').all()[:10]:
            user = profile.user
            resolved = base_qs.filter(assigned_to=user, status__in=['resolu', 'cloture']).count()
            active = profile.active_tickets_count
            avg_note = TicketEvaluation.objects.filter(
                ticket__assigned_to=user
            ).aggregate(avg=Avg('note'))['avg']
            techniciens_perf.append({
                'id': user.id,
                'name': user.get_full_name(),
                'resolved_count': resolved,
                'active_count': active,
                'avg_rating': round(avg_note, 1) if avg_note else None,
                'is_available': profile.is_available,
            })

        # Tickets par zone
        tickets_by_zone = []
        for zone in Zone.objects.filter(is_active=True):
            commune_ids = zone.communes.values_list('id', flat=True)
            quartier_ids = zone.quartiers.values_list('id', flat=True)
            count = base_qs.filter(
                Q(pharmacie__commune_id__in=commune_ids) |
                Q(pharmacie__quartier_id__in=quartier_ids)
            ).count()
            if count > 0:
                tickets_by_zone.append({'zone': zone.name, 'count': count})

        # Évolution mensuelle (6 derniers mois)
        six_months_ago = now - timedelta(days=180)
        try:
            monthly_evolution = list(
                base_qs.filter(created_at__gte=six_months_ago)
                .annotate(month=TruncMonth('created_at'))
                .values('month')
                .annotate(count=Count('id'))
                .order_by('month')
                .values('month', 'count')
            )
        except (ValueError, Exception):
            # Fallback for SQLite + USE_TZ: group manually
            from collections import Counter
            tickets_qs = base_qs.filter(created_at__gte=six_months_ago).values_list('created_at', flat=True)
            month_counts = Counter()
            for dt in tickets_qs:
                if dt:
                    month_counts[dt.strftime('%Y-%m-01')] += 1
            monthly_evolution = [
                {'month': k, 'count': v}
                for k, v in sorted(month_counts.items())
            ]

        return Response({
            'tickets_total': base_qs.count(),
            'tickets_this_month': tickets_this_month,
            'tickets_by_status': tickets_by_status,
            'tickets_by_urgence': tickets_by_urgence,
            'avg_resolution_hours': avg_resolution,
            'avg_rating': round(avg_rating, 1) if avg_rating else None,
            'pharmacies_count': Pharmacie.objects.count(),
            'techniciens_count': TechnicienProfile.objects.count(),
            'techniciens_available': TechnicienProfile.objects.filter(is_available=True).count(),
            'techniciens_performance': techniciens_perf,
            'tickets_by_zone': tickets_by_zone,
            'monthly_evolution': monthly_evolution,
        })


class PharmacyDashboardView(APIView):
    """Tableau de bord pour une pharmacie."""
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Dashboard'])
    def get(self, request):
        user = request.user
        if user.is_pharmacie:
            tickets = Ticket.objects.filter(pharmacie__user=user)
        elif user.is_admin:
            pharmacy_id = request.query_params.get('pharmacy_id')
            if pharmacy_id:
                tickets = Ticket.objects.filter(pharmacie_id=pharmacy_id)
            else:
                tickets = Ticket.objects.all()
        else:
            tickets = Ticket.objects.none()

        by_status = dict(
            tickets.values_list('status').annotate(c=Count('id')).values_list('status', 'c')
        )
        by_urgence = dict(
            tickets.values_list('urgence').annotate(c=Count('id')).values_list('urgence', 'c')
        )

        return Response({
            'total': tickets.count(),
            'by_status': by_status,
            'by_urgence': by_urgence,
            'open_count': tickets.exclude(status__in=['resolu', 'cloture']).count(),
            'resolved_count': tickets.filter(status__in=['resolu', 'cloture']).count(),
        })


class TechnicianDashboardView(APIView):
    """Tableau de bord pour un technicien."""
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Dashboard'])
    def get(self, request):
        user = request.user
        if user.is_technicien:
            tech_user = user
        elif user.is_admin:
            tech_id = request.query_params.get('technicien_id')
            if tech_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    tech_user = User.objects.get(pk=tech_id, role='technicien')
                except User.DoesNotExist:
                    return Response({'detail': 'Technicien introuvable.'}, status=404)
            else:
                return Response({'detail': 'technicien_id requis.'}, status=400)
        else:
            return Response({'detail': 'Non autorisé.'}, status=403)

        tickets = Ticket.objects.filter(assigned_to=tech_user)
        rapports = RapportIntervention.objects.filter(technicien=tech_user)

        # Optional pharmacy filter
        pharmacie_id = request.query_params.get('pharmacie')
        if pharmacie_id:
            tickets = tickets.filter(pharmacie_id=pharmacie_id)
            rapports = rapports.filter(ticket__pharmacie_id=pharmacie_id)

        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month = tickets.filter(created_at__gte=month_start)

        eval_qs = TicketEvaluation.objects.filter(ticket__assigned_to=tech_user)
        if pharmacie_id:
            eval_qs = eval_qs.filter(ticket__pharmacie_id=pharmacie_id)
        avg_note = eval_qs.aggregate(avg=Avg('note'))['avg']

        return Response({
            'total_assigned': tickets.count(),
            'active_count': tickets.filter(status__in=['assigne', 'en_cours', 'en_attente']).count(),
            'resolved_count': tickets.filter(status__in=['resolu', 'cloture']).count(),
            'this_month_count': this_month.count(),
            'rapports_count': rapports.count(),
            'avg_rating': round(avg_note, 1) if avg_note else None,
            'by_status': dict(
                tickets.values_list('status').annotate(c=Count('id')).values_list('status', 'c')
            ),
        })


class ExportView(APIView):
    """Export des tickets en CSV/Excel."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(tags=['Dashboard'])
    def get(self, request):
        import csv
        from django.http import HttpResponse

        format_type = request.query_params.get('format', 'csv')
        status_filter = request.query_params.get('status')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        tickets = Ticket.objects.select_related('pharmacie', 'assigned_to', 'created_by').all()

        if status_filter:
            tickets = tickets.filter(status=status_filter)
        if date_from:
            tickets = tickets.filter(created_at__date__gte=date_from)
        if date_to:
            tickets = tickets.filter(created_at__date__lte=date_to)

        if format_type == 'excel':
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Tickets SAV"
            headers = [
                'Référence', 'Objet', 'Catégorie', 'Urgence', 'Statut',
                'Pharmacie', 'Technicien', 'Type intervention',
                'Créé le', 'Résolu le',
            ]
            ws.append(headers)
            for t in tickets:
                ws.append([
                    t.reference, t.objet, t.get_categorie_display(),
                    t.get_urgence_display(), t.get_status_display(),
                    t.pharmacie.nom_pharmacie if t.pharmacie else '',
                    t.assigned_to.get_full_name() if t.assigned_to else '',
                    t.get_type_intervention_display(),
                    t.created_at.strftime('%Y-%m-%d %H:%M') if t.created_at else '',
                    t.resolved_at.strftime('%Y-%m-%d %H:%M') if t.resolved_at else '',
                ])
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=tickets_sav.xlsx'
            wb.save(response)
            return response

        # CSV par défaut
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename=tickets_sav.csv'
        response.write('\ufeff')  # BOM UTF-8

        writer = csv.writer(response, delimiter=';')
        writer.writerow([
            'Référence', 'Objet', 'Catégorie', 'Urgence', 'Statut',
            'Pharmacie', 'Technicien', 'Type intervention',
            'Créé le', 'Résolu le',
        ])
        for t in tickets:
            writer.writerow([
                t.reference, t.objet, t.get_categorie_display(),
                t.get_urgence_display(), t.get_status_display(),
                t.pharmacie.nom_pharmacie if t.pharmacie else '',
                t.assigned_to.get_full_name() if t.assigned_to else '',
                t.get_type_intervention_display(),
                t.created_at.strftime('%Y-%m-%d %H:%M') if t.created_at else '',
                t.resolved_at.strftime('%Y-%m-%d %H:%M') if t.resolved_at else '',
            ])
        return response
