# core/tasks.py
import os
import logging
from datetime import datetime, timedelta
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task
def send_saved_form_reminders():
    """
    Scans the saved_forms folder and sends a reminder email for any file that is older than 3 days.
    Filename format is expected to be:
        username_saved_YYYYMMDD_HHMMSS_XXXX
    """
    # Directory for saved forms inside the media folder
    saved_forms_dir = os.path.join(settings.MEDIA_ROOT, 'saved_forms')
    now = datetime.now()
    reminder_threshold = now - timedelta(days=3)
    
    logger.info("Running send_saved_form_reminders task.")
    logger.info("Scanning directory: %s", saved_forms_dir)
    
    if not os.path.exists(saved_forms_dir):
        logger.warning("Directory %s does not exist.", saved_forms_dir)
        return

    # Loop through files in the directory
    for filename in os.listdir(saved_forms_dir):
        logger.debug("Processing file: %s", filename)
        # Expected filename format: "username_saved_YYYYMMDD_HHMMSS_XXXX"
        parts = filename.split('_')
        if len(parts) < 4:
            logger.warning("Filename %s does not match expected pattern.", filename)
            continue

        username = filename.split('_saved_')[0]
        date_str = parts[-3]  # e.g., "20250228"
        time_str = parts[-2]  # e.g., "135241"
        try:
            file_datetime = datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")
        except ValueError as ve:
            logger.error("Error parsing date/time from filename %s: %s", filename, ve)
            continue

        logger.debug("Parsed datetime: %s; Threshold: %s", file_datetime, reminder_threshold)

        # If the file is older than the threshold, send a reminder email.
        if file_datetime <= reminder_threshold:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                logger.warning("User with username %s not found.", username)
                continue

            subject = "Reminder: Submit Your Saved Form"
            message = (
                f"Hi {username},\n\n"
                f"You saved a form on {file_datetime.strftime('%Y-%m-%d %H:%M:%S')}. "
                "Please complete and submit it as soon as possible.\n\n"
                "Thank you!"
            )
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                logger.info("Reminder email sent to %s (%s).", username, user.email)
            except Exception as e:
                logger.error("Error sending email to %s: %s", username, e)
        else:
            logger.debug("File %s is newer than threshold; no email sent.", filename)

    logger.info("send_saved_form_reminders task completed.")

