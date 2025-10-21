from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'transactions'

router = DefaultRouter()
router.register('transactions', views.TransactionViewSet, basename='transaction')

urlpatterns = [
    path('transactions/upload', views.TransactionUploadView.as_view(), name='upload-transactions'),

    path('reports/customer-summary/<uuid:customer_id>', views.ReportCustomerSummaryView.as_view(), name='report-customer-summary'),
    path('reports/product-summary/<uuid:product_id>', views.ReportProductSummaryView.as_view(), name='report-product-summary'),

    path('', include(router.urls)),
]
