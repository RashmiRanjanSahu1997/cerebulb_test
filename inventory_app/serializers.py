from rest_framework import serializers
from .models import Product, Category, Supplier, StockLog

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class StockLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockLog
        fields = '__all__'
