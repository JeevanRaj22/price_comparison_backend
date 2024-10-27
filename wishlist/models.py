from django.db import models
from login.models import CustomUser

class Product(models.Model):
    amazon_name = models.CharField(max_length=255)
    flipkart_name = models.CharField(max_length=255)
    image = models.URLField(max_length=500)
    amazon_url = models.URLField(max_length=500)
    flipkart_url = models.URLField(max_length=500)
    amazon_price = models.DecimalField(max_digits=10, decimal_places=2)
    flipkart_price = models.DecimalField(max_digits=10, decimal_places=2)
    ram = models.CharField(max_length=100,default=None)  # New field for RAM
    rom = models.CharField(max_length=100,default=None)  # New field for ROM
    color = models.CharField(max_length=100,default=None)  # New field for Color
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amazon_name} vs {self.flipkart_name}"


class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wishlists')
    products = models.ManyToManyField(Product, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist of {self.user.username}"

class PriceCheckTracker(models.Model):
    task_name = models.CharField(max_length=255, unique=True)
    last_run = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.task_name
