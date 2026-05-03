from django.db import models
from django.utils import timezone

class Customer(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=20)
    mobile = models.CharField(max_length=10)
    address = models.CharField(max_length=50)

    def __str__(self):
        return self.username

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_status=models.CASCADE, related_name='orders')
    items = models.TextField() # Can store a summary of ordered items
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer.username}"

class Activity(models.Model):
    user_name = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Activities"

    @property
    def time_ago(self):
        return "Today" 

    def __str__(self):
        return f"{self.user_name} - ${self.amount}"


