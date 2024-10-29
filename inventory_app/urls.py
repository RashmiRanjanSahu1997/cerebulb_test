from django.urls import path
from .views import (
    ProductListCreateAPIView,
    ProductDetailAPIView,
    ManageStockAPIView,
    StockAlertAPIView,
    InventoryReportAPIView,SignupAPIView, LoginAPIView
)

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('products/<int:product_id>/manage-stock/', ManageStockAPIView.as_view(), name='manage-stock'),
    path('stock-alerts/', StockAlertAPIView.as_view(), name='stock-alerts'),
    path('inventory-report/', InventoryReportAPIView.as_view(), name='inventory-report'),
]
