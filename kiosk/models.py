from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='manager')

    def is_admin(self):
        return self.role == 'admin'


class Supplier(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    item_supplied = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    balance_owed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_purchase = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date_added = models.DateField(auto_now_add=True)
    last_transaction_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-date_added']


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('payment', 'Payment'),
        ('purchase', 'Purchase'),
    ]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    item = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.supplier.name} - Ksh {self.amount}"

    class Meta:
        ordering = ['-created_at']
