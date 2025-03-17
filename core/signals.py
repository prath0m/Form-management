
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CustomUser, FormUpload, PreviousFinding, FormSubmission
from google.cloud import bigquery


CUSTOM_USER_TABLE = 'dfsp-prototype.project_dataset.CustomUser'
FORM_UPLOAD_TABLE = 'dfsp-prototype.project_dataset.FormUpload'
def get_form_submission_data(instance):
    """Convert a FormSubmission instance into a dict matching your BigQuery table schema."""
    return {
        "id": instance.id,
        "user_id": instance.user.id,
        "form_type": instance.form_type,
        "submitted_file": instance.submitted_file,
        "file_path": instance.file_path,
        "submitted_at": instance.submitted_at.isoformat() if instance.submitted_at else None,
    }

@receiver(post_save, sender=FormSubmission)
def handle_form_submission_post_save(sender, instance, created, **kwargs):
    form_data = get_form_submission_data(instance)
    client = bigquery.Client()
    table_id = CUSTOM_USER_TABLE
    if created:
        try:
            rows_to_insert = [form_data]
            errors = client.insert_rows_json(table_id, rows_to_insert)
            if errors:
                print("Encountered errors while inserting rows into BigQuery: {}".format(errors))
            else:
                print("Data inserted into BigQuery table successfully.")
        except Exception as bq_error:
            print("BigQuery insertion error:", bq_error)
    else:
        # Update: run an update query in BigQuery.
        try:
            query = f"""
                UPDATE {table_id}
                SET form_type = @form_type,
                    submitted_file = @submitted_file,
                    file_path = @file_path,
                    submitted_at = @submitted_at
                WHERE id = @id
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("form_type", "STRING", form_data["form_type"]),
                    bigquery.ScalarQueryParameter("submitted_file", "STRING", form_data["submitted_file"]),
                    bigquery.ScalarQueryParameter("file_path", "STRING", form_data["file_path"]),
                    bigquery.ScalarQueryParameter("submitted_at", "TIMESTAMP", form_data["submitted_at"]),
                    bigquery.ScalarQueryParameter("id", "INT64", form_data["id"]),
                ]
            )
            query_job = client.query(query, job_config=job_config)
            query_job.result()  # Wait for the query to complete.
            print("Data updated in BigQuery table successfully.")
        except Exception as bq_error:
            print("BigQuery update error:", bq_error)

@receiver(post_delete, sender=FormSubmission)
def handle_form_submission_post_delete(sender, instance, **kwargs):
    client = bigquery.Client()
    table_id = FORM_UPLOAD_TABLE
    try:
        query = f"""
            DELETE FROM {table_id}
            WHERE id = @id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("id", "INT64", instance.id),
            ]
        )
        query_job = client.query(query, job_config=job_config)
        query_job.result()  # Wait for the query to complete.
        print("Data deleted from BigQuery table successfully.")
    except Exception as bq_error:
        print("BigQuery deletion error:", bq_error)
def get_custom_user_data(instance):
    """
    Convert a CustomUser instance into a dict matching your BigQuery table schema.
    Adjust the fields here if your BigQuery table requires additional data.
    """
    return {
        "id": instance.id,
        "username": instance.username,
        "role": instance.role,
        "is_authorized": instance.is_authorized,
        "status": instance.status,
    }

@receiver(post_save, sender=CustomUser)
def handle_custom_user_post_save(sender, instance, created, **kwargs):
    print('custom user create signal triggered')
    user_data = get_custom_user_data(instance)
    client = bigquery.Client()
    table_id = CUSTOM_USER_TABLE

    if created:
        # Create: Insert a new row into BigQuery.
        try:
            rows_to_insert = [user_data]
            errors = client.insert_rows_json(table_id, rows_to_insert)
            if errors:
                print("Encountered errors while inserting CustomUser row into BigQuery: {}".format(errors))
            else:
                print("CustomUser data inserted into BigQuery table successfully.")
        except Exception as bq_error:
            print("BigQuery insertion error for CustomUser:", bq_error)
    else:
        # Update: Execute an UPDATE query in BigQuery.
        try:
            query = f"""
                UPDATE {table_id}
                SET username = @username,
                    role = @role,
                    is_authorized = @is_authorized,
                    status = @status
                WHERE id = @id
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("username", "STRING", user_data["username"]),
                    bigquery.ScalarQueryParameter("role", "STRING", user_data["role"]),
                    bigquery.ScalarQueryParameter("is_authorized", "BOOL", user_data["is_authorized"]),
                    bigquery.ScalarQueryParameter("status", "STRING", user_data["status"]),
                    bigquery.ScalarQueryParameter("id", "INT64", user_data["id"]),
                ]
            )
            query_job = client.query(query, job_config=job_config)
            query_job.result()  # Wait for query completion
            print("CustomUser data updated in BigQuery table successfully.")
        except Exception as bq_error:
            print("BigQuery update error for CustomUser:", bq_error)

@receiver(post_delete, sender=CustomUser)
def handle_custom_user_post_delete(sender, instance, **kwargs):
    client = bigquery.Client()
    table_id =CUSTOM_USER_TABLE
    try:
        query = f"""
            DELETE FROM {table_id}
            WHERE id = @id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("id", "INT64", instance.id),
            ]
        )
        query_job = client.query(query, job_config=job_config)
        query_job.result()  # Wait for query completion
        print("CustomUser data deleted from BigQuery table successfully.")
    except Exception as bq_error:
        print("BigQuery deletion error for CustomUser:", bq_error)
