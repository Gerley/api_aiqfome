

## 🍕 API de Integração aiqfome

Este projeto é uma aplicação **Django REST API** containerizada com **PostgreSQL**, **autenticação JWT** e **documentação automática via Swagger**.

O container aplica as migrações automaticamente e cria um superusuário caso não exista.

---

### 💻 Pricipais Tecnologias utilizadas:
* [Python 3.12](https://www.python.org/): Liguagem de programação;
* [Django](https://www.djangoproject.com/): Princiapal framework de desenvolvimento de aplicações web com a linguagem Python;
* [Django REST Framework](https://www.django-rest-framework.org/): Extende o framework Django para utilizar protocolo REST;
* [Django REST Framework SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/): Implementa a autenticação via JWT;
* [drf-yasg (Swagger UI)](https://drf-yasg.readthedocs.io/): Utilizada para documentar a API;
* [PostgreSQL](https://www.postgresql.org/): Banco de dados da aplicação;
* [Docker](https://www.docker.com/): Tecnologia de containers utilizada para isolar o ambiente da aplicação;
* [Docker Compose](https://docs.docker.com/compose/): Tecnologia utilizada para integração dos containers da aplicação: Container App Web, Container Data Base.

---

### 📂 Estrutura do projeto

```
.
├── api_aiqfome/
│   ├── manage.py
│   ├── api_aiqfome/
│   ├── custom_auth/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── customers/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests/
│   └── ...
├── Dockerfile
├── compose.yml
├── entrypoint.sh
├── requirements.txt
└── README.md

```

---

### 🚀 Como rodar o projeto

1. **Build e inicialização dos containers:**

```bash
sudo docker compose up
```

2. O Django irá:

* Esperar o banco de dados estar pronto
* Aplicar as migrações (`python manage.py migrate`)
* Criar o superusuário (se não existir)

3. A API estará disponível em:

```
http://127.0.0.1:8000
```

4. Faça a autenticação via o endpoint **/auth/login** com os parametros **username:** "admin" e **password:** "123456"

---

### 🌐 Endpoints principais

#### 🔐 Autenticação JWT

| Método | Endpoint              | Descrição                     |
| ------ | --------------------- | ----------------------------- |
| POST   | `/auth/login`         | Gera um token JWT (login).    |
| POST   | `/auth/refresh`      | Atualiza o token JWT.         |
| POST   | `/auth/logout`       | Adiciona o refresh token na blacklist. |

#### 👥 Clientes (`customers`)

| Método    | Endpoint           | Descrição                                                                           |
| --------- | ------------------ | ----------------------------------------------------------------------------------- |
| GET    | `/customers/`      | Lista todos os clientes.|
| POST   | `/customers/`      | Cria um novo cliente.|
| GET    | `/customers/{id}/` | Retorna detalhes de um cliente específico.|
| PUT    | `/customers/{id}/` | Atualiza dados de um cliente.|
| DELETE | `/customers/{id}/` | Remove um cliente.|

#### ⭐ Produtos favoritos

| Método | Endpoint                             | Descrição                                        |
| ------ | ------------------------------------ | ------------------------------------------------ |
| GET    | `/customers/favorite-products/`      | Lista produtos favoritos do cliente autenticado.|
| POST   | `/customers/favorite-products/`      | Adiciona um produto aos favoritos.|
| DELETE | `/customers/favorite-products/{id}/` | Remove um produto dos favoritos.|

#### 📕 Documentação Swagger

* Swagger UI:

```
http://127.0.0.1:8000/swagger/
```

---

### 🧪 Testes

Para executar os testes via docker, primeiramente, levante os containers:
```bash
sudo docker compose up -d
```

Execute os testes:

```bash
sudo docker exec api python manage.py test
```

Isso executará todos os testes definidos em `app/customers/tests.py`.

---

### 📝 Principais decisões de Projeto
* Toda a parte de autenticação foi deixado a cargo do "Django REST Framework SimpleJWT", ele já possui funcionalidades para login, logout e refresh token.
* Para a integração com a API externa, foi adotada um esquema de cache para que a aplicação não tenha que ficar todo momento solicitando os dados da API Externa.
* Para a modelagem de dados do cliente, foi utilizado o model User que já vem com Django.
* Para a modelagem da lista de produtos favoritos, foi criado um model que possui apenas 2 atributos, user (associado ao model User, ou cliente) e product_id (associado ao id do produto da API externa).
