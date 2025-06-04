from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db.models import Sum, Count, F 

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model): 
    seller = models.ForeignKey(User,on_delete=models.CASCADE,related_name='products')
    name = models.CharField(max_length=255)
    desc = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    file = models.FileField(upload_to='uploads', default='uploads/no_image.png')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def number_of_sales(self):
        # Sum of quantity from all OrderItems related to this product
        result = self.orderitem_set.aggregate(total_quantity=Sum('quantity'))
        return result['total_quantity'] or 0

    def number_of_orders(self):
        # Count of distinct orders that include this product
        result = self.orderitem_set.aggregate(total_orders=Count('order', distinct=True))
        return result['total_orders'] or 0

    def total_sales_price(self):
        # Sum of quantity * price for all OrderItems of this product
        result = self.orderitem_set.aggregate(
            total_sales=Sum(F('quantity') * F('price'))
        )
        return result['total_sales'] or 0
    def __str__(self):
        return self.name

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} wishes {self.product.name}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.user.username} - {self.product.name} (x{self.quantity})"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} -- {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # store price at the time of order

    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f'{self.pk} ---- {self.product.name}'
