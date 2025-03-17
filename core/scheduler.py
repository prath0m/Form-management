# core/scheduler.py
import time
import logging
from django.conf import settings
from core.tasks import send_saved_form_reminders

logger = logging.getLogger(__name__)

def run_scheduler():
    # Set sleep interval to 3 days in seconds.
    sleep_interval = 3 * 24 * 60 * 60  # For testing, you might use a shorter interval (e.g., 60 seconds)
    
    while True:
        logger.info("Scheduler: Starting send_saved_form_reminders task.")
        try:
            # You can choose to call the task synchronously:
            send_saved_form_reminders()
            # ...or if you use Celery, call it asynchronously:
            # send_saved_form_reminders.delay()
        except Exception as e:
            logger.exception("Scheduler encountered an error: %s", e)
        logger.info("Scheduler: Task completed. Sleeping for %s seconds.", sleep_interval)
        time.sleep(sleep_interval)
