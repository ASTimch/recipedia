# Рецептурная энциклопедия


## Учебный проект "Рецептурная энциклопедия"

Позволяет пользователям публиковать свои рецепты, подписываться на других пользователей, формировать подборки избранных рецептов и перечня продуктов, необходимых для приготовления выбранных рецептов.
Технологии: 
- Python 
- Django DRF
- PostgreSQL
- Docker
- Docker Compose

### Как запустить проект:

Клонировать репозиторий и перейти в папку проекта в командной строке:

```
git clone git@github.com:ASTimch/recipedia.git
```

Подготовить в папке проекта infra/ файл .env с переменными окружения по примеру .env.example

```
POSTGRES_DB=<Наименование_базы_данных>
POSTGRES_USER=<Имя_пользователя_базы_данных>
POSTGRES_PASSWORD=<Пароль_пользователя_базы_данных>
DB_HOST=database
DB_PORT=5342
SECRET_KEY = "django-insecure-code"
DEBUG = "False"
ALLOWED_HOSTS = "127.0.0.1 localhost hostname"
```

Перейти в папку проекта infra/ и выполнить запуск проекта на базе Docker-контейнеров 
(предварительно убедитесь, что запущен Docker daemon):
```
cd infra
sudo docker compose up
```

Выполнить миграции бэкенда. 

```
sudo docker compose exec backend python manage.py migrate
```

Выполнить сбор и подготовку статических файлов бэкенда. 

```
sudo docker compose exec backend python manage.py collectstatic

sudo docker compose exec backend cp -r /app/collected_static/. /static_backend
```

Создать учетную запись суперпользователя. 

```
sudo docker compose exec backend python manage.py createsuperuser

```

Для инициализации базы данных списком ингредиентов:

```
sudo docker compose exec backend python manage.py load_tags --file ./data/tags.csv
sudo docker compose exec backend python manage.py load_ingredients --file ./data/ingredients.csv
```

Проект доступен по адресу

```
http://localhost/
```

Документация по API проекта доступна по адресу
```
http://localhost/docs/swagger/
http://localhost/docs/redoc/
```

Для завершения работы оркестра контейнеров
```
sudo docker compose down
```
