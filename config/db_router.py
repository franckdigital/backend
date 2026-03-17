"""
Database router for dual MySQL setup:
- 'default' (sav_pharmacie) : Django models, read/write
- 'windev'  (FacturationClient) : WinDev legacy, READ-ONLY

Le VPS Django se connecte au MySQL du serveur WinDev via réseau.
Django n'écrit JAMAIS dans la base WinDev.
"""


class WindevRouter:
    """
    Route toutes les opérations Django vers 'default'.
    La base 'windev' est utilisée uniquement via des raw SQL
    dans apps.windev_sync.services (curseur explicite).
    """

    # Apps qui n'existent que dans la base Django
    django_apps = {
        'accounts', 'pharmacies', 'tickets', 'zones',
        'interventions', 'notifications', 'dashboard',
        'windev_sync',
        # Django built-in
        'admin', 'auth', 'contenttypes', 'sessions',
        'token_blacklist',
    }

    def db_for_read(self, model, **hints):
        """Toutes les lectures Django vont vers 'default'."""
        return 'default'

    def db_for_write(self, model, **hints):
        """Toutes les écritures Django vont vers 'default'."""
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Relations uniquement entre objets de la même base."""
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Les migrations ne s'appliquent que sur 'default'.
        La base 'windev' est gérée par WinDev, pas par Django.
        """
        if db == 'windev':
            return False
        return True
