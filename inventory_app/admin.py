from django.contrib import admin
from .models import Product, Category, Supplier, StockLog
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(StockLog)
# Register your models here.
