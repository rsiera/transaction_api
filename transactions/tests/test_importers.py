from pathlib import Path

import pytest
from celery import states
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from transactions.importers import CSVImporter
from transactions.models import Transaction
from transactions.tests.factories import FileImportRequestFactory

User = get_user_model()


def get_sample_file(filename):
    current_dir = Path(__file__).resolve().parent
    file_path = current_dir / 'samples' / filename

    with open(file_path, 'rb') as f:
        return SimpleUploadedFile(
            name=filename,
            content=f.read(),
            content_type='text/csv'
        )


@pytest.mark.django_db
class TestCSVImporter:
    def test_import_file_should_save_exception_meta_and_failure_when_invalid_file(self):
        file_request = FileImportRequestFactory.create(file='')
        with CSVImporter(file_request.id) as csv_importer:
            csv_importer.import_file()

        file_request.refresh_from_db()

        assert file_request.status == states.FAILURE
        assert file_request.exception_meta == {
            'exception_type': "<class 'ValueError'>",
            'exception_value': "The 'file' attribute has no file associated with it."
        }

    def test_import_file_should_import_valid_and_log_invalid_and_success(self):
        csv_file = get_sample_file('invalid_transactions.csv')
        file_request = FileImportRequestFactory.create(file=csv_file)
        with CSVImporter(file_request.id) as csv_importer:
            csv_importer.import_file()

        file_request.refresh_from_db()

        assert file_request.status == states.SUCCESS
        assert file_request.exception_meta == {}
        assert Transaction.objects.count() == 1
        assert Transaction.objects.get(id='550e8400-e29b-41d4-a716-446655440020')

    def test_import_file_should_import_multiple_valid_and_success(self):
        csv_file = get_sample_file('valid_transactions.csv')
        file_request = FileImportRequestFactory.create(file=csv_file)
        with CSVImporter(file_request.id) as csv_importer:
            csv_importer.import_file()

        file_request.refresh_from_db()

        assert file_request.status == states.SUCCESS
        assert file_request.exception_meta == {}
        assert Transaction.objects.all().count() == 5
