import uuid
from unittest import mock

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from transactions.choices import CurrencyChoices
from transactions.tests.factories import UserFactory, TransactionFactory
from transactions.tests.test_importers import get_sample_file


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_client_with_authenticated():
    user = UserFactory()
    token = Token.objects.create(user=user)
    client = APIClient()
    client.force_authenticate(user, token)
    return client


@pytest.mark.django_db
class TestTransactionUploadView:
    def test_post_should_return_401_when_no_authenticated(self, api_client):
        url = reverse("transactions:upload-transactions")
        payload = {"file": get_sample_file("valid_transactions.csv")}

        response = api_client.post(url, payload)

        assert response.status_code == 401

    @mock.patch("transactions.api.serializers.import_csv_task.delay")
    def test_post_should_handle_file_when_ok(self, mock_import_csv_task_delay, api_client_with_authenticated):
        url = reverse("transactions:upload-transactions")

        payload = {"file": get_sample_file("valid_transactions.csv")}

        response = api_client_with_authenticated.post(url, payload)

        assert response.status_code == 201
        mock_import_csv_task_delay.assert_called_once()


@pytest.mark.django_db
class TestReportCustomerSummaryView:
    def test_get_should_return_401_when_no_authenticated(self, api_client):
        customer_id = uuid.uuid4()
        url = reverse("transactions:report-customer-summary", args=(customer_id,))

        response = api_client.get(url)

        assert response.status_code == 401

    def test_get_should_return_empty_aggregated_when_no_transactions(self, api_client_with_authenticated):
        customer_id = uuid.uuid4()
        url = reverse("transactions:report-customer-summary", args=(customer_id,))

        response = api_client_with_authenticated.get(url)

        assert response.status_code == 200
        assert response.data["total_cost_in_pln"] == "0.00"
        assert response.data["count_distinct_product"] == 0
        assert response.data["last_transaction_datetime"] is None

    def test_get_should_return_filtered_aggregated_when_transactions_exists(self, api_client_with_authenticated):
        customer_id = uuid.uuid4()
        now = timezone.now()
        TransactionFactory(
            customer_id=customer_id,
            currency=CurrencyChoices.PLN,
            amount=100,
            amount_in_pln=100,
            product_id=uuid.uuid4(),
            quantity=2,
            timestamp=now,

        )
        TransactionFactory(
            customer_id=customer_id,
            currency=CurrencyChoices.EUR,
            amount=100,
            amount_in_pln=400,
            product_id=uuid.uuid4(),
            quantity=2,
            timestamp=now,
        )
        TransactionFactory(
            customer_id=uuid.uuid4(),
            currency=CurrencyChoices.EUR,
            amount=2200,
            amount_in_pln=8800,
            product_id=uuid.uuid4(),
            quantity=2,
            timestamp=now,

        )
        url = reverse("transactions:report-customer-summary", args=(customer_id,))

        response = api_client_with_authenticated.get(url)

        assert response.status_code == 200
        assert response.data["total_cost_in_pln"] == "1000.00"
        assert response.data["count_distinct_product"] == 2
        assert response.data["last_transaction_datetime"] == now.isoformat().replace("+00:00", "Z")


@pytest.mark.django_db
class TestReportProductSummaryView:
    def test_get_should_return_401_when_no_authenticated(self, api_client):
        product_id = uuid.uuid4()
        url = reverse("transactions:report-product-summary", args=(product_id,))

        response = api_client.get(url)

        assert response.status_code == 401

    def test_get_should_return_empty_aggregated_when_no_transactions(self, api_client_with_authenticated):
        product_id = uuid.uuid4()
        url = reverse("transactions:report-product-summary", args=(product_id,))

        response = api_client_with_authenticated.get(url)

        assert response.status_code == 200
        assert response.data["sum_quantity"] == 0
        assert response.data["count_distinct_customer"] == 0
        assert response.data["total_income_in_pln"] == "0.00"

    def test_get_should_return_filtered_aggregated_when_transactions_exists(self, api_client_with_authenticated):
        product_id = uuid.uuid4()
        now = timezone.now()
        TransactionFactory(
            customer_id=uuid.uuid4(),
            currency=CurrencyChoices.PLN,
            amount=100,
            amount_in_pln=100,
            product_id=product_id,
            quantity=2,
            timestamp=now,

        )
        TransactionFactory(
            customer_id=uuid.uuid4(),
            currency=CurrencyChoices.EUR,
            amount=100,
            amount_in_pln=400,
            product_id=product_id,
            quantity=2,
            timestamp=now,
        )
        TransactionFactory(
            customer_id=uuid.uuid4(),
            currency=CurrencyChoices.EUR,
            amount=2200,
            amount_in_pln=8800,
            product_id=uuid.uuid4(),
            quantity=2,
            timestamp=now,

        )
        url = reverse("transactions:report-product-summary", args=(product_id,))

        response = api_client_with_authenticated.get(url)

        assert response.status_code == 200
        assert response.data["sum_quantity"] == 4
        assert response.data["count_distinct_customer"] == 2
        assert response.data["total_income_in_pln"] == "1000.00"
