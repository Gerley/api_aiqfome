import os
import requests
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from drf_yasg.utils import swagger_serializer_method
from django.contrib.auth.models import User
from django.core.cache import cache
from json.decoder import JSONDecodeError

from .models import FavoriteProduct


class CustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(required=True)
    last_name =  serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'is_staff']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
        
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class FavoriteProductSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    title = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    rating_rate = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()


    class Meta:
        model = FavoriteProduct
        fields = ['id', 'user', 'product_id', 'title', 'image', 'price', 'rating_rate', 'rating_count']

    def create(self, validated_data):
        user = self.context['request'].user
        product_id = validated_data['product_id']

        cached_product = self._get_cached_product(product_id)
        if not cached_product:
            raise serializers.ValidationError("Produto não encontrado")

        favorite = FavoriteProduct.objects.create(
            user=user,
            product_id=product_id
        )
        return favorite

    def to_representation(self, instance):
        instance._cached_product = self._get_cached_product(instance.product_id) or {}
        return super().to_representation(instance)

    def _get_cached_product(self, product_id):
        try:
            cached_product = cache.get(f'product_{product_id}')
            if cached_product:
                return cached_product

            url = os.getenv("URL_EXTERNAL_API")
            if not url:
                return None

            response = requests.get(f"{url}/{product_id}")
            if response.status_code == 200:
                cached = response.json()
                cache.set(f'product_{product_id}', cached, timeout=3600)
                return cached
            return None
        except JSONDecodeError:
            raise serializers.ValidationError("Produto não encontrado")

    @swagger_serializer_method(
        serializer_or_field=serializers.CharField(help_text="Breve descrição do produto")
    )
    def get_title(self, obj):
        return obj._cached_product.get('title') if hasattr(obj, '_cached_product') else None

    @swagger_serializer_method(
        serializer_or_field=serializers.CharField(help_text="Um link da imagem do produto")
    )    
    def get_image(self, obj):
        return obj._cached_product.get('image') if hasattr(obj, '_cached_product') else None

    @swagger_serializer_method(
        serializer_or_field=serializers.FloatField(help_text="Preço do produto")
    )
    def get_price(self, obj):
        return obj._cached_product.get('price') if hasattr(obj, '_cached_product') else None

    @swagger_serializer_method(
        serializer_or_field=serializers.FloatField(help_text="Avaliação do produto")
    )
    def get_rating_rate(self, obj):
        return obj._cached_product.get('rating').get('rate') if hasattr(obj, '_cached_product') else None

    @swagger_serializer_method(
        serializer_or_field=serializers.IntegerField(help_text="Quantidade de avaliações do produto")
    )
    def get_rating_count(self, obj):
        return obj._cached_product.get('rating').get('count') if hasattr(obj, '_cached_product') else None
