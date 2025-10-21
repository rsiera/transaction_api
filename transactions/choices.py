from django.db import models


class CurrencyChoices(models.TextChoices):
    PLN = "PLN", "PLN"
    EUR = "EUR", "EUR"
    USD = "USD", "USD"
