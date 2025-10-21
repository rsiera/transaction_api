from django.db import models
from django.db.models import Count, Max, F, Sum, DecimalField
from django.db.models.functions import Coalesce


class TransactionManager(models.Manager):
    def for_customer(self, customer_id):
        return self.filter(customer_id=customer_id)

    def for_product(self, product_id):
        return self.filter(product_id=product_id)

    def group_by_customer(self, customer_id):
        transactions = self.for_customer(customer_id)

        aggregated = transactions.aggregate(
            count_distinct_product=Coalesce(Count('product_id', distinct=True), 0),
            last_transaction_datetime=Max('timestamp'),
            total_cost_in_pln=Coalesce(
                Sum(F('amount_in_pln') * F('quantity')),
                0.0,
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
        )

        return {
            'total_cost_in_pln': aggregated['total_cost_in_pln'],
            'count_distinct_product': aggregated['count_distinct_product'],
            'last_transaction_datetime': aggregated['last_transaction_datetime'],
        }

    def group_by_product(self, product_id):
        transactions = self.for_product(product_id)

        aggregated = transactions.aggregate(
            sum_quantity=Coalesce(Sum('quantity'), 0),
            count_distinct_customer=Coalesce(Count('customer_id', distinct=True), 0),
            total_income_in_pln=Coalesce(
                Sum(F('amount_in_pln') * F('quantity')),
                0.0,
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
        )

        return {
            'sum_quantity': aggregated['sum_quantity'],
            'count_distinct_customer': aggregated['count_distinct_customer'],
            'total_income_in_pln': aggregated['total_income_in_pln'],
        }
