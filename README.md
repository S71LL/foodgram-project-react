### Как развернуть проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:S71LL/foodgram-project-react.git
```

```
cd foodgram-project-react
```

Создайте файл .env в репозитории:

```
touch .env
```

Пример содержания файла:

POSTGRES_DB=django
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mypassword
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
SECRET_KEY=mysecretkey
DEBUG=True
ALLOWED_HOSTS=localhost

Запустите docker compose:

```
sudo docker compose -f docker-compose.production.yml up -d
```

Выполнить миграции:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

Запустите скрипт импорта заготовленных ингредиентов в базу данных:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py csvimport
```

Выполните сбор статики:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

Скопируйте статику в необходимую дерикторию:

```
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

Проект доступен локально
## http://localhost

[![Main foodgram workflow](https://github.com/S71LL/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/S71LL/foodgram-project-react/actions/workflows/main.yml)
