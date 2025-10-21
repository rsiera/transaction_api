import csv
import io
import logging
from decimal import Decimal

from celery import states
from django.db import transaction
from django.utils import timezone

from rest_framework import serializers

from .consts import EXCHANGE_RATES
from .models import FileImportRequest, Transaction

logger = logging.getLogger(__name__)


class ImportTransactionSerializer(serializers.ModelSerializer):
    amount_in_pln = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        read_only=False
    )

    transaction_id = serializers.UUIDField(required=True, source='id')

    class Meta:
        model = Transaction
        fields = [
            'transaction_id',
            'timestamp',
            'amount',
            'amount_in_pln',
            'currency',
            'customer_id',
            'product_id',
            'quantity',
        ]

    def validate(self, data):
        data['amount_in_pln'] = self.get_amount_in_pln(data['currency'], data['amount'])
        return data

    def get_amount_in_pln(self, currency, amount):
        if currency not in EXCHANGE_RATES:
            logger.warning('Currency "%s" no exchange rate', currency)
        return amount * EXCHANGE_RATES.get(currency, Decimal("1.0"))


class CSVImporter:
    def __init__(self, import_request_id):
        self.import_request_id = import_request_id

    def __enter__(self):
        self.import_request = FileImportRequest.objects.get(pk=self.import_request_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.import_request.status = states.FAILURE
            self.import_request.exception_meta = {
                'exception_type': str(exc_type),
                'exception_value': str(exc_val),
            }
        else:
            self.import_request.status = states.SUCCESS
        self.import_request.completed_at = timezone.now()
        self.import_request.save()
        return True

    def import_file(self):
        file_content = self.import_request.file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(file_content))

        valid_transactions = []
        for line in csv_reader:
            serializer = ImportTransactionSerializer(data=line)
            if not serializer.is_valid():
                logger.warning(f"Invalid data: %s, file_request: %s", line, self.import_request_id)
                continue

            valid_transactions.append(Transaction(**serializer.validated_data))

        with transaction.atomic():
            Transaction.objects.bulk_create(valid_transactions)
