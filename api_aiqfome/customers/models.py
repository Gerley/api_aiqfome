from django.db import models
from django.contrib.auth.models import User


class FavoriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_products')
    product_id = models.BigIntegerField(help_text="Identificador do Produto", default=1)

    class Meta:
        unique_together = ('user', 'product_id')

    def __str__(self):
        return f"{self.user.username} -> {self.product.name}"