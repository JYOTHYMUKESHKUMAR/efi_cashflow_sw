from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from datetime import timedelta
import datetime
from django.db.models import Sum
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
# from django.db.models import F, ExpressionWrapper, DecimalField
from django.core.exceptions import ValidationError
from decimal import Decimal
import json

class CustomUser(AbstractUser):
    USER_TYPES = (
        
        ('1', 'Account Team'),
        ('2', 'Manager'),
        ('3', 'Admin'),
         # If you need a superuser/admin role
    )

    user_type = models.CharField(choices=USER_TYPES, max_length=50, default='ACCOUNT_TEAM')
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True, null=True)

class IncomeSource(models.Model):
    name = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return self.name
class ExpenseSource(models.Model):
    name= models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return self.name


class CashIn(models.Model):
    
    STATUS_CHOICES = [
        ('Received', 'Received'),
        ('Scheduled', 'Scheduled'),
    ]
    
    COST_CENTER_CHOICES = [
        ('catalyst', 'Catalyst'),
        ('oil_and_gas', 'Oil and Gas'),
        ('general_chemicals', 'General Chemicals'),
        ('overhead', 'Overhead'),
    ]
    
    income_source = models.ForeignKey(IncomeSource, on_delete=models.DO_NOTHING)
    date = models.DateField()
    cash_in = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Received')
    remark = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, blank=True, null=True)
    cost_center = models.CharField(max_length=50, choices=COST_CENTER_CHOICES, default='catalyst', blank=True, null=True)
    service_date = models.DateField(blank=True, null=True)

    

    def __str__(self):
        return f"Cash In - {self.date} - {self.cash_in}"
    
    




class Cashout(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Scheduled', 'Scheduled'),
    ]

    COST_CENTER_CHOICES = [
        ('catalyst', 'Catalyst'),
        ('oil_and_gas', 'Oil and Gas'),
        ('general_chemicals', 'General Chemicals'),
        ('overhead', 'Overhead'),
    ]

    expense_source = models.ForeignKey(ExpenseSource, on_delete=models.DO_NOTHING)
    date = models.DateField()
    cash_out = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Paid')
    remark = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, blank=True, null=True)
    cost_center = models.CharField(max_length=50, choices=COST_CENTER_CHOICES, default='catalyst', blank=True, null=True)
    service_date = models.DateField()
    installment_details = models.JSONField(blank=True, null=True)
    total_installment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    balance_to_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def update_installments(self, installment_details):
        print("update_installments method called")

        if not installment_details:
            raise ValidationError("Installment details cannot be empty")

        # Parse the JSON string into a Python dictionary
        if isinstance(installment_details, str):
            installment_details = json.loads(installment_details)

        print("Current cash_out value:", self.cash_out)
        print("Current total_installment_amount:", self.total_installment_amount)

        total_amount = Decimal(0)
        for installment in installment_details:
            installment_amount = Decimal(installment['amount'])
            print("Adding installment amount:", installment_amount)
            total_amount += installment_amount

        print("Total installment amount after calculation:", total_amount)

        cash_out_decimal = Decimal(self.cash_out)
        print("Cash out (Decimal):", cash_out_decimal)

        balance_to_pay = cash_out_decimal - total_amount
        print("Balance to pay:", balance_to_pay)

        self.installment_details = installment_details
        self.total_installment_amount = total_amount
        self.balance_to_pay = balance_to_pay
        self.save()

    def __str__(self):
        return f"Cashout {self.id}"
    

class Summary(models.Model):
    date = models.DateField(unique=True)
    cash_in = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    cash_out = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return str(self.date)


class ProjectSummary(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateField()
    cash_in = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    cash_out = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    service_date = models.DateField()

    def __str__(self):
        return f"Summary for {self.project} on {self.date}"

# class Inventory(models.Model):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)
#     total_cash_in = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
#     total_cash_out = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
#     balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
#     start_inventory = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
#     end_inventory = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
#     actual_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

#     def __str__(self):
#         return f"Inventory for {self.project}"