from django.apps import AppConfig

    
    
    
# core/apps.py
import sys
import threading
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):

        # To avoid running the scheduler during migrations or in shell, check if runserver is in sys.argv.
        if "runserver" in sys.argv:
            import core.signals
            from .scheduler import run_scheduler
            # Start the scheduler in a daemon thread so it stops when the main process stops.
            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()

