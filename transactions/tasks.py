import logging

from celery import shared_task

from .importers import CSVImporter

logger = logging.getLogger(__name__)


@shared_task()
def import_csv_task(import_log_id):
    with CSVImporter(import_log_id) as csv_importer:
        csv_importer.import_file()
    logger.info(f"CSV completed for file request: {import_log_id}")