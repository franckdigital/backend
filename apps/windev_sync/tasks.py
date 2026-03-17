"""
Tâches Celery pour la synchronisation périodique bidirectionnelle.

Planning Celery Beat (configuré dans settings.py) :
  - sync_windev_to_django_incremental : toutes les 2 min
  - sync_django_to_windev_incremental : toutes les 2 min
  - sync_windev_referentials           : toutes les 15 min
"""
import logging
from celery import shared_task
from django.conf import settings

logger = logging.getLogger('windev_sync')


def _windev_configured():
    """Vérifie que la connexion WinDev est configurée."""
    return 'windev' in settings.DATABASES


# ═══════════════════════════════════════════════════════════
#  TÂCHES PÉRIODIQUES (appelées par Celery Beat)
# ═══════════════════════════════════════════════════════════

@shared_task(bind=True, name='apps.windev_sync.tasks.sync_windev_to_django_incremental',
             max_retries=2, default_retry_delay=30)
def sync_windev_to_django_incremental(self):
    """
    WinDev → Django (toutes les 2 minutes).
    Lit les nouveaux/modifiés dans FacturationClient
    et les importe dans sav_pharmacie.
    """
    if not _windev_configured():
        return {'skipped': 'windev DB not configured'}

    try:
        from .services import run_windev_to_django_incremental
        result = run_windev_to_django_incremental()
        logger.info(f"WinDev→Django sync: {result}")
        return result
    except Exception as exc:
        logger.error(f"WinDev→Django sync failed: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, name='apps.windev_sync.tasks.sync_django_to_windev_incremental',
             max_retries=2, default_retry_delay=30)
def sync_django_to_windev_incremental(self):
    """
    Django → WinDev (toutes les 2 minutes).
    Exporte les nouveaux tickets/rapports de sav_pharmacie
    vers FacturationClient + met à jour les statuts.
    """
    if not _windev_configured():
        return {'skipped': 'windev DB not configured'}

    try:
        from .services import run_django_to_windev_incremental
        result = run_django_to_windev_incremental()
        logger.info(f"Django→WinDev sync: {result}")
        return result
    except Exception as exc:
        logger.error(f"Django→WinDev sync failed: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, name='apps.windev_sync.tasks.sync_windev_referentials',
             max_retries=1, default_retry_delay=60)
def sync_windev_referentials(self):
    """
    Sync référentiels WinDev → Django (toutes les 15 minutes).
    Villes, localités (données qui changent rarement).
    """
    if not _windev_configured():
        return {'skipped': 'windev DB not configured'}

    try:
        from .services import run_windev_referentials
        result = run_windev_referentials()
        logger.info(f"WinDev referentials sync: {result}")
        return result
    except Exception as exc:
        logger.error(f"WinDev referentials sync failed: {exc}")
        raise self.retry(exc=exc)


# ═══════════════════════════════════════════════════════════
#  TÂCHES MANUELLES (déclenchables via l'API)
# ═══════════════════════════════════════════════════════════

@shared_task(name='apps.windev_sync.tasks.sync_full')
def sync_full():
    """Synchronisation complète bidirectionnelle (manuelle)."""
    if not _windev_configured():
        return {'skipped': 'windev DB not configured'}

    from .services import run_full_sync
    result = run_full_sync()
    logger.info(f"Full bidirectional sync: {result}")
    return result
