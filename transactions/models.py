import logging
import uuid

from celery import states
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from .choices import CurrencyChoices
from .managers import TransactionManager

logger = logging.getLogger(__name__)


class Transaction(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    timestamp = models.DateTimeField(db_index=True)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    amount_in_pln = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(max_length=3, choices=CurrencyChoices.choices)
    customer_id = models.UUIDField(db_index=True)
    product_id = models.UUIDField(db_index=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    created_at = models.DateTimeField(auto_now_add=True)

    objects = TransactionManager()

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['customer_id', 'timestamp']),
            models.Index(fields=['product_id', 'timestamp']),
        ]

    def __str__(self):
        return f"Transaction[{self.id}] {self.amount} {self.currency}"


class FileImportRequest(models.Model):
    ALL_STATES = sorted(states.ALL_STATES)
    TASK_STATE_CHOICES = sorted(zip(ALL_STATES, ALL_STATES))

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=50,
        default=states.PENDING,
        choices=TASK_STATE_CHOICES,
        verbose_name='Import Status',
    )
    file = models.FileField(
        upload_to='import_requests/%Y/%m',
        blank=True,
        max_length=150,
    )
    exception_meta = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return (
            f'FileImportRequest[id={self.id} status={self.status}'
        )
