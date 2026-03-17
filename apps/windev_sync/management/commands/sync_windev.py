"""
Commande de management pour la synchronisation bidirectionnelle WinDev <-> Django.

Usage :
    python manage.py sync_windev                     # Sync complete bidirectionnelle
    python manage.py sync_windev --windev-to-django   # WinDev -> Django seulement
    python manage.py sync_windev --django-to-windev   # Django -> WinDev seulement
    python manage.py sync_windev --referentials       # Referentiels (localites)
    python manage.py sync_windev --reset-cursors      # Reinitialiser les curseurs

Crontab (toutes les 2 minutes) :
    */2 * * * * cd /path/to/backend && /path/to/venv/bin/python manage.py sync_windev >> /var/log/sav_sync.log 2>&1
"""
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Synchronisation bidirectionnelle WinDev <-> Django (sav_pharmacie <-> FacturationClient)'

    def add_arguments(self, parser):
        parser.add_argument('--windev-to-django', action='store_true',
                            help='Sync incrementale WinDev -> Django')
        parser.add_argument('--django-to-windev', action='store_true',
                            help='Sync incrementale Django -> WinDev')
        parser.add_argument('--referentials', action='store_true',
                            help='Sync referentiels (villes, localites)')
        parser.add_argument('--reset-cursors', action='store_true',
                            help='Reinitialiser les curseurs (force re-sync complete)')

    def _print_results(self, label, results):
        """Affiche les resultats d'une sync."""
        if isinstance(results, dict) and all(isinstance(v, dict) for v in results.values()):
            for entity, result in results.items():
                synced = result.get('synced', 0)
                failed = result.get('failed', 0)
                style = self.style.SUCCESS if failed == 0 else self.style.WARNING
                self.stdout.write(style(
                    f'  {label}/{entity}: {synced} sync, {failed} echec'
                ))
        else:
            synced = results.get('synced', 0)
            failed = results.get('failed', 0)
            style = self.style.SUCCESS if failed == 0 else self.style.WARNING
            self.stdout.write(style(f'  {label}: {synced} sync, {failed} echec'))

    def handle(self, *args, **options):
        if 'windev' not in settings.DATABASES:
            self.stderr.write(self.style.ERROR(
                'Base WinDev non configuree. Definir WINDEV_DB_NAME dans .env'
            ))
            return

        if options['reset_cursors']:
            from apps.windev_sync.models import SyncCursor
            count = SyncCursor.objects.all().update(last_synced_id=0, last_synced_at=None)
            self.stdout.write(self.style.SUCCESS(f'{count} curseur(s) reinitialise(s).'))
            return

        specific = options['windev_to_django'] or options['django_to_windev'] or options['referentials']

        try:
            if options['windev_to_django']:
                self.stdout.write('WinDev -> Django (incremental)...')
                from apps.windev_sync.services import run_windev_to_django_incremental
                self._print_results('WD->DJ', run_windev_to_django_incremental())

            elif options['django_to_windev']:
                self.stdout.write('Django -> WinDev (incremental)...')
                from apps.windev_sync.services import run_django_to_windev_incremental
                self._print_results('DJ->WD', run_django_to_windev_incremental())

            elif options['referentials']:
                self.stdout.write('Referentiels WinDev -> Django...')
                from apps.windev_sync.services import run_windev_referentials
                self._print_results('REF', run_windev_referentials())

            else:
                self.stdout.write('Synchronisation complete bidirectionnelle...')
                from apps.windev_sync.services import run_full_sync
                results = run_full_sync()
                for section, data in results.items():
                    self._print_results(section, data)

            self.stdout.write(self.style.SUCCESS('Termine.'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erreur: {e}'))
