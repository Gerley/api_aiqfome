from django.contrib.auth.models import User
from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import FavoriteProduct
from .serializers import CustomerSerializer, FavoriteProductSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser] 
    queryset = User.objects.all()
    serializer_class = CustomerSerializer
    http_method_names = ['get', 'post', 'put', 'delete']


    @swagger_auto_schema(
        operation_summary="Lista todos os clientes",
        responses={
            200: openapi.Response('', CustomerSerializer),
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden'
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Cria o registro de um cliente",
        request_body=CustomerSerializer,
        responses={
            201: openapi.Response('', CustomerSerializer),
            400: "Error: Bad Request",
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden'
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Obtem o registro de um cliente",
        responses={
            200: openapi.Response('', CustomerSerializer),
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            404: 'Error: Not Found',
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Atualiza o registro de um cliente",
        request_body=CustomerSerializer,
        responses={
            200: openapi.Response('', CustomerSerializer),
            400: "Error: Bad Request",
            401: 'Error: Unauthorized',
            404: 'Error: Not Found',
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
  
    @swagger_auto_schema(
        operation_summary="Desativa o registro de um cliente",
        responses={
            200: "Usuário desativado",
            401: 'Error: Unauthorized',
            404: 'Error: Not Found',
        },
    )
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"detail": "Usuário desativado."}, status=status.HTTP_200_OK)


class FavoriteProductViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteProductSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return FavoriteProduct.objects.none() 
            
        return FavoriteProduct.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        request_body=FavoriteProductSerializer,
        operation_summary="Adiciona um produto aos favoritos",
        responses={
            201: FavoriteProductSerializer,
            401: 'Error: Unauthorized',
            404: 'Error: Not Found',
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Lista os produtos favoritos",
        responses={
            200: FavoriteProductSerializer(many=True),
            401: 'Error: Unauthorized'
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Remove o produto dos favoritos",
        responses={
            204: 'No Content',
            401: 'Error: Unauthorized',
            404: 'Error: Not Found',
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)