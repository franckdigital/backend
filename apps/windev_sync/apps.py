import threading
import logging
from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger('windev_sync')


class WindevSyncConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.windev_sync'
    verbose_name = 'Synchronisation WinDev'

    def ready(self):
        """Lance la synchronisation périodique en background thread si la DB WinDev est configurée."""
        if not getattr(settings, 'DATABASES', {}).get('windev'):
            return

        # Avoid running twice (Django reloader)
        import os
        if os.environ.get('RUN_MAIN') != 'true' and not os.environ.get('WINDSURF_SYNC'):
            return

        interval = getattr(settings, 'SYNC_INTERVAL_SECONDS', 120)
        if interval and interval > 0:
            t = threading.Thread(target=self._run_periodic_sync, args=(interval,), daemon=True)
            t.start()
            logger.info(f"Auto-sync thread started (every {interval}s)")

    @staticmethod
    def _run_periodic_sync(interval):
        """Boucle de synchronisation périodique."""
        import time
        # Wait for Django to fully initialize
        time.sleep(10)
        while True:
            try:
                from .services import run_windev_to_django_incremental, run_django_to_windev_incremental
                logger.info("Auto-sync: WinDev → Django")
                run_windev_to_django_incremental()
                logger.info("Auto-sync: Django → WinDev")
                run_django_to_windev_incremental()
                logger.info("Auto-sync cycle complete")
            except Exception as e:
                logger.error(f"Auto-sync error: {e}")
            time.sleep(interval)
