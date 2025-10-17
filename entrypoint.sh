#!/bin/sh

set -e

# Espera o banco de dados ficar disponível
echo "Esperando o banco de dados..."
until nc -z db 5432; do
  sleep 1
done
echo "Banco de dados pronto!"

# Aplica migrações
echo "Executando migrações..."
python manage.py migrate --noinput

# Cria superusuário se não existir
echo "Verificando se o superusuário existe..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
username = "admin"
email = "admin@example.com"
password = "123456"
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superusuário '{username}' criado.")
else:
    print(f"Superusuário '{username}' já existe.")
END

# Executa o comando principal do container (ex: runserver)
exec "$@"
