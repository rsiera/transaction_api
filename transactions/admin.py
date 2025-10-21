from django.contrib import admin

from .models import FileImportRequest, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "timestamp",
        "amount",
        "amount_in_pln",
        "currency",
        "customer_id",
        "product_id",
        "quantity",
        "created_at",
    ]
    list_filter = ["customer_id", "product_id"]


@admin.register(FileImportRequest)
class FileImportRequestAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "status",
        "processed_at",
    ]
    list_filter = ["status"]
