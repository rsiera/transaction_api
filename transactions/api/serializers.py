from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from ..models import Transaction, FileImportRequest
from ..tasks import import_csv_task


class CSVFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(
        required=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['csv']),

        ]
    )

    def create(self, validated_data):
        import_request = FileImportRequest.objects.create(
            requested_by=self.context["request"].user,
            file=validated_data["file"],
        )
        import_csv_task.delay(import_request.id)
        return import_request


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id',
            'timestamp',
            'amount',
            'currency',
            'customer_id',
            'product_id',
            'quantity',
            'created_at'
        ]
        read_only_fields = ['created_at']


class ReportCustomerSummarySerializer(serializers.Serializer):
    total_cost_in_pln = serializers.DecimalField(max_digits=12, decimal_places=2)
    count_distinct_product = serializers.IntegerField()
    last_transaction_datetime = serializers.DateTimeField()


class ReportProductSummarySerializer(serializers.Serializer):
    sum_quantity = serializers.IntegerField()
    total_income_in_pln = serializers.DecimalField(max_digits=12, decimal_places=2)
    count_distinct_customer = serializers.IntegerField()
