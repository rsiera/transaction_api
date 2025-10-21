from decimal import Decimal

from transactions.choices import CurrencyChoices

EXCHANGE_RATES = {
    CurrencyChoices.PLN: Decimal('1.0'),
    CurrencyChoices.EUR: Decimal('4.3'),
    CurrencyChoices.USD: Decimal('4.0'),
}
