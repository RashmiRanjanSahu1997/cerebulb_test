# models.py
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.TextField()

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    sku = models.CharField(max_length=100, unique=True)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class StockLog(models.Model):
    ACTION_CHOICES = [('add', 'Add'), ('remove', 'Remove')]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    action = models.CharField(max_length=6, choices=ACTION_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()

    def __str__(self):
        return f"{self.product.name} - {self.quantity} ({self.get_action_display()})"
