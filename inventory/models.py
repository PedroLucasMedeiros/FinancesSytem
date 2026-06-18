from django.db import models
from core.models import BaseModel

class Product(BaseModel):
    name = models.CharField(max_length=20, null=False)
    description = models.CharField(max_length=100, null=False)
    imagem = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return self.name
    
class Sale(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_unity_retail = models.DecimalField(max_digits=10, decimal_places=2)
    price_unity_wholesale = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Sale of {self.product.name} - Quantity: {self.quantity}"