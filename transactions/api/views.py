from django_filters import rest_framework as filters

from rest_framework import viewsets, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser

from .serializers import (
    TransactionSerializer,
    ReportCustomerSummarySerializer,
    ReportProductSummarySerializer,
    CSVFileUploadSerializer
)
from ..models import Transaction


class RangeTransactionFilter(filters.FilterSet):
    date_from = filters.DateTimeFilter(field_name="timestamp", lookup_expr="gte")
    date_to = filters.DateTimeFilter(field_name="timestamp", lookup_expr="lte")


class TransactionPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class TransactionUploadView(generics.CreateAPIView):
    serializer_class = CSVFileUploadSerializer
    parser_classes = (MultiPartParser,)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.all()
    pagination_class = TransactionPagination
    serializer_class = TransactionSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ("customer_id", "product_id",)
    lookup_field = 'transaction_id'


class ReportCustomerSummaryView(generics.RetrieveAPIView):
    serializer_class = ReportCustomerSummarySerializer
    lookup_field = "customer_id"
    filterset_class = RangeTransactionFilter

    def get_object(self):
        return Transaction.objects.group_by_customer(self.kwargs["customer_id"])


class ReportProductSummaryView(generics.RetrieveAPIView):
    serializer_class = ReportProductSummarySerializer
    lookup_field = "product_id"
    filterset_class = RangeTransactionFilter

    def get_object(self):
        return Transaction.objects.group_by_product(self.kwargs["product_id"])
