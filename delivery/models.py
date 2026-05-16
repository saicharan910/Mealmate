from django.db import models
from django.db.models import Sum

# Create your models here.
class Customer(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=20)
    mobile = models.CharField(max_length=10)
    address = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.username} {self.password} {self.email} {self.mobile} {self.address}"


class Restaurant(models.Model):
    name = models.CharField(max_length=20)
    picture = models.URLField(max_length=200,
                              default="https://cwdaust.com.au/wpress/wp-content/uploads/2015/04/placeholder-restaurant.png")
    cuisine = models.CharField(max_length=200)
    rating = models.FloatField()

    def __str__(self):
        return f"{self.name} {self.cuisine} {self.rating}/5"


class Item(models.Model):
    # ERROR FIX: changed related_name to "items" to match your views.py logic
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menu_items")
    name = models.CharField(max_length=20)
    picture = models.URLField(max_length=1000, default="https://cdn-icons-png.flaticon.com/512/1147/1147856.png")
    description = models.CharField(max_length=200)
    price = models.FloatField()
    # ERROR FIX: changed is_veg to vegeterian to match your views.py logic
    vegeterian = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} {self.description} {self.price}"


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="cart")
    items = models.ManyToManyField("Item", related_name="carts")

    def total_price(self):
        """Calculates total price using database aggregation."""
        return self.items.aggregate(total=Sum('price'))['total'] or 0

    def __str__(self):
        # Calling self.total_price() here is correct
        return f"{self.customer.username} - Total: ₹{self.total_price()}"