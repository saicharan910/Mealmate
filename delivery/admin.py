from django.contrib import admin

from .models import Customer, Order, Activity

# Register your models here.
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Activity)
