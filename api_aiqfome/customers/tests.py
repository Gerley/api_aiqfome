import os
import requests
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from django.db.models import Max

from customers.models import FavoriteProduct


class CustomerIntegrationTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Criação do usuario adm
        User.objects.create_user(username='admin', email='admin@example.com', password='123456', is_staff=True)

        # Criação do usuario não adm
        User.objects.create_user(username='user', email='user@example.com', password='123456')

    def setUp(self):
        self.client = APIClient()

    def authenticate(self, username, password):
        """Autenticação e configuração do token."""
        response = self.client.post('/auth/login', {'username': username, 'password': password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_list_customers_without_authenticated(self):
        """Usuário não autenticado não deve acessar o endpoint '/customers/'"""
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_customers_with_user_adm(self):
        """Usuário adm pode acessar o endpoint '/customers/' """
        self.authenticate('admin', '123456')

        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # endpoint deve retornar os dois usuarios cadastrados no banco
        response_data = response.json()
        self.assertEqual(len(response_data), 2)


    def test_list_customers_with_user_not_adm(self):
        """Usuário comum não deve acessar o endpoint '/customers/'"""
        self.authenticate('user', '123456')
        
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_customers_without_authenticated(self):
        """Usuário não autenticado não deve criar um novo usuário"""
        payload = {
            "username": "user_test",
            "email": "usertest@example.com",
            "password": "password",
            "first_name": "first_name",
            "last_name": "last_name"
        }
        response = self.client.post('/customers/', payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_customers_with_user_not_adm(self):
        """Usuário comum não deve criar um novo usuário"""
        self.authenticate('user', '123456')

        payload = {
            "username": "user_test",
            "email": "usertest@example.com",
            "password": "password",
            "first_name": "first_name",
            "last_name": "last_name"
        }
        response = self.client.post('/customers/', payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_customers_with_user_adm(self):
        """Usuário admin deve criar um novo usuário"""
        self.authenticate('admin', '123456')

        payload = {
            "username": "user_test",
            "email": "usertest@example.com",
            "password": "password",
            "first_name": "first_name",
            "last_name": "last_name"
        }
        response = self.client.post('/customers/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_customers_required_field(self):
        """Os campos nome e email são obrigatórios"""
        self.authenticate('admin', '123456')

        payload = {
            "username": "user_test",
            "password": "password",
        }
        response = self.client.post('/customers/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
        response_data = response.json()
        for field in ['email', 'first_name', 'last_name']:
            self.assertIn(field, response_data)
            self.assertIn('This field is required.', response_data[field])

    def test_create_customers_duplicated_email(self):
        """Um mesmo e-mail não pode se repetir no cadastro"""
        User.objects.create_user(
            username='user_test', 
            email='usertest@example.com', 
            password='123456',
            first_name="first_name",
            last_name="last_name"
        )

        self.authenticate('admin', '123456')

        # tenta crair o segundo usuario com email duplicado
        payload = {
            "username": "user_test2",
            "email": "usertest@example.com",
            "password": "password",
            "first_name": "first_name2",
            "last_name": "last_name2"
        }
        response = self.client.post('/customers/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.json()
        self.assertIn('email', response_data)
        self.assertIn('This field must be unique.', response_data['email'])

    
    def test_retrieve_customers_without_authenticated(self):
        """Usuário não autenticado não deve acessar o endpoint '/customers/{id}'"""

        user = User.objects.create_user(username='user_test', email='usertest@example.com', password='123456')

        response = self.client.get(f'/customers/{user.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_retrieve_customers_with_user_not_adm(self):
        """Usuário comum não deve acessar o endpoint '/customers/{id}'"""
        user = User.objects.create_user(username='user_test', email='usertest@example.com', password='123456')

        self.authenticate('user', '123456')
        
        response = self.client.get(f'/customers/{user.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_customers_with_user_adm(self):
        """Usuário adm pode acessar o endpoint '/customers/{id}' """
        user = User.objects.create_user(username='user_test', email='usertest@example.com', password='123456')

        self.authenticate('admin', '123456')

        response = self.client.get(f'/customers/{user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_customers_not_found_user(self):
        """Usuário não existe no banco de dados"""
        max_id = User.objects.aggregate(max_id=Max('id'))
        invalid_id = max_id['max_id'] + 1

        self.authenticate('admin', '123456')

        response = self.client.get(f'/customers/{invalid_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_customers_without_authenticated(self):
        """Usuário não autenticado não deve alterar outro usuario"""

        user = User.objects.create_user(username='user_test', email='usertest@example.com', password='123456')

        payload = {
            "username": "user_test2",
            "email": "usertest@example.com",
            "password": "password",
            "first_name": "first_name2",
            "last_name": "last_name2"
        }

        response = self.client.put(f'/customers/{user.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_customers_with_user_not_adm(self):
        """Usuário comum não deve alterar outro usuario"""
        user = User.objects.create_user(username='user_test', email='usertest@example.com', password='123456')

        self.authenticate('user', '123456')

        payload = {
            "username": "user_test2",
            "email": "usertest@example.com",
            "password": "password",
            "first_name": "first_name2",
            "last_name": "last_name2"
        }

        response = self.client.put(f'/customers/{user.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_customers_with_user_adm(self):
        """Usuário adm deve alterar outro usuario"""
        user = User.objects.create_user(username='user_test', email='usertest@example.com', password='123456')

        self.authenticate('admin', '123456')

        payload = {
            "username": "user_test2",
            "email": "usertest@example.com",
            "password": "password",
            "first_name": "first_name2",
            "last_name": "last_name2"
        }

        response = self.client.put(f'/customers/{user.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_customers_not_found_user(self):
        """Usuário não existe no banco de dados"""
        max_id = User.objects.aggregate(max_id=Max('id'))
        invalid_id = max_id['max_id'] + 1

        self.authenticate('admin', '123456')

        payload = {
            "username": "user_test2",
            "email": "usertest@example.com",
            "password": "password",
            "first_name": "first_name2",
            "last_name": "last_name2"
        }

        response = self.client.put(f'/customers/{invalid_id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_customers_required_field(self):
        """Os campos nome e email são obrigatórios"""
        user = User.objects.create_user(username='user_test', email='usertest@example.com', password='123456')

        self.authenticate('admin', '123456')

        payload = {
            "username": "user_test",
            "password": "password",
        }
        response = self.client.put(f'/customers/{user.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
        response_data = response.json()
        for field in ['email', 'first_name', 'last_name']:
            self.assertIn(field, response_data)
            self.assertIn('This field is required.', response_data[field])

    def test_update_customers_duplicated_email(self):
        """Um mesmo e-mail não pode se repetir no cadastro"""
        User.objects.create_user(username='user_test', email='usertest@example.com', password='123456')

        user = User.objects.create_user(username='user_test2', email='usertest2@example.com', password='123456')

        self.authenticate('admin', '123456')

        # tenta crair o segundo usuario com email duplicado
        payload = {
            "username": "user_test2",
            "email": "usertest@example.com",
            "password": "password",
            "first_name": "first_name2",
            "last_name": "last_name2"
        }
        response = self.client.put(f'/customers/{user.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.json()
        self.assertIn('email', response_data)
        self.assertIn('This field must be unique.', response_data['email'])

    def test_delete_customers_without_authenticated(self):
        """Usuário não autenticado não deve remover usuarios"""
        user = User.objects.create_user(username='user_test', email='usertest@example.com', password='123456')

        response = self.client.delete(f'/customers/{user.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_customers_with_user_not_adm(self):
        """Usuário comum não deve remover usuarios"""
        user = User.objects.create_user(username='user_test', email='usertest@example.com', password='123456')

        self.authenticate('user', '123456')

        response = self.client.delete(f'/customers/{user.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_customers_with_user_adm(self):
        """Usuário adm deve remover usuarios"""
        user = User.objects.create_user(username='user_test', email='usertest@example.com', password='123456')

        self.authenticate('admin', '123456')

        response = self.client.delete(f'/customers/{user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_customers_not_found_user(self):
        """Usuário não existe no banco de dados"""
        max_id = User.objects.aggregate(max_id=Max('id'))
        invalid_id = max_id['max_id'] + 1

        self.authenticate('admin', '123456')

        response = self.client.delete(f'/customers/{invalid_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FavoriteProductsIntegrationTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Criação do usuario não adm
        User.objects.create_user(username='user', email='user@example.com', password='123456')

    def setUp(self):
        self.client = APIClient()

    def authenticate(self, username, password):
        """Autenticação e configuração do token."""
        response = self.client.post('/auth/login', {'username': username, 'password': password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_list_favorite_products_without_authenticated(self):
        """Usuário não autenticado não deve listar produtos favoritos"""
        response = self.client.get(f'/customers/favorite-products/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_favorite_products_with_authenticated(self):
        """Usuário autenticado deve listar produtos favoritos"""
        user = User.objects.get(username='user')

        url = os.getenv("URL_EXTERNAL_API")
        response = requests.get(url)
        products = response.json()[:3]

        for product in products:
            FavoriteProduct.objects.create(
                user=user,
                product_id=product['id']
            )

        self.authenticate('user', '123456')

        response = self.client.get(f'/customers/favorite-products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        
        # verifica se possui três itens na lista conforme foi adicionado no banco
        self.assertEqual(3, len(response_data))

        # verifica os campos de retorno do produto
        product_response = response_data[0]
        for field in ['product_id', 'title', 'image', 'price', 'rating_rate', 'rating_count']:
            self.assertIn(field, product_response)

    def test_list_favorite_products_empty(self):
        """Usuário não possui lista de favoritos"""
        self.authenticate('user', '123456')

        response = self.client.get(f'/customers/favorite-products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    def test_create_favorite_products_without_authenticated(self):
        """Usuário não autenticado não deve criar produtos favoritos"""
        payload = {
            'product_id': 1
        }
        response = self.client.post(f'/customers/favorite-products/', payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_favorite_products_with_authenticated(self):
        """Usuário autenticado deve criar produtos favoritos"""
        self.authenticate('user', '123456')

        payload = {
            'product_id': 1
        }
        response = self.client.post(f'/customers/favorite-products/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_favorite_products_invalid_product_id(self):
        """Não deve criar favorico com id de produto inválido"""
        # Gera um id de produto que não existe na API externa
        url = os.getenv("URL_EXTERNAL_API")
        response = requests.get(url)
        product_ids = [product['id'] for product in response.json()]
        invalid_product_id = max(product_ids) + 1 if len(product_ids) else 1
        
        self.authenticate('user', '123456')

        payload = {
            'product_id': invalid_product_id
        }
        response = self.client.post(f'/customers/favorite-products/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn('Produto não encontrado', response.json())
    
    def test_delete_favorite_products_without_authenticated(self):
        """Usuário não autenticado não deve remover produtos favoritos"""
        response = self.client.delete(f'/customers/favorite-products/1/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_favorite_products_with_authenticated(self):
        """Usuário autenticado deve remover produtos favoritos"""
        user = User.objects.get(username='user')

        url = os.getenv("URL_EXTERNAL_API")
        response = requests.get(url)
        product = response.json()[0]

        favoriteProduct = FavoriteProduct.objects.create(
            user=user,
            product_id=product['id']
        )

        self.authenticate('user', '123456')

        id = favoriteProduct.id
        response = self.client.delete(f'/customers/favorite-products/{id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_favorite_products_invalid_id(self):
        """Não deve remover produto favorito com id inválido"""
        self.authenticate('user', '123456')

        response = self.client.delete('/customers/favorite-products/1/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
