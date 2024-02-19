# Проект Foodgram

### Foodgram - это социальная сеть для обмена рецептами. Реализована возможность регистрации, создания своих рецептов, подписки на пользователей и составления списка покупок по ингредиентам из рецептов в корзине

Для проекта реализован CI/CD. Автоматическое размещение и запуск проекта на удаленном сервере выполняется при пуше в ветку master. Для корректной работы необходимо, чтобы на удаленном сервере в дериктории проетка был файл .env (пример приведен в блоке локально развертки), а также необходимо задать секретные переменные в настройках репозитория на GitHub. Помимо этого на удаленном сервере нужно настроить nginx

Необходимые секретные переменные:
- DOCKER_PASSWORD - пароль от аккаунта Docker Hub
- DOCKER_USERNAME - username на Docker Hub
- HOST - ip-адрес удаленного сервера
- SSH_KEY - закрытый SSH ключ
- SSH_PASSPHRASE - пароль от SSH ключа
- TELEGRAM_TO - id в телеграме для отправки сообщения об успешном деплое
- TELEGRAM_TOKEN - токен бота в телеграме
- USER - username на удаленном сервере

Пример настройки nginx на удаленном сервере:

```
server {
    listen 80;
    server_name ip_удаленного_сервера;

    location / {
        proxy_pass http:/127.0.0.1:8000;
    }

}
```

### Как развернуть проект локально:

Сделать форк репозитория

Клонировать репозиторий, заменв username на имя пользователя и перейти в него в командной строке:

```
git clone git@github.com:username/foodgram-project-react.git
```

```
cd foodgram-project-react
```

Создать файл .env в репозитории и заполнить его:

```
touch .env
```

Пример содержания файла:

```
POSTGRES_DB=django
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mypassword
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
SECRET_KEY=mysecretkey
DEBUG=True
ALLOWED_HOSTS=localhost
```

Запустите docker compose:

```
docker compose -f docker-compose.yml up -d
```

Выполнить миграции:

```
docker compose -f docker-compose.yml exec backend python manage.py migrate
```

Запустить скрипт импорта заготовленных ингредиентов в базу данных:

```
docker compose -f docker-compose.yml exec backend python manage.py csvimport
```

Выполнить сбор статики:

```
docker compose -f docker-compose.yml exec backend python manage.py collectstatic
```


Проект доступен локально
### http://localhost:8000

### Как открыть документацию:

Выполнить клонирование репозитория и перейти в дерикторию foodgram-project-react

Перейти в дерикторию infra и запустить docker compose

```
cd infra
docker compose up
```

Документация доступна по адресу
### http://localhost/api/docs/

[![Main foodgram workflow](https://github.com/S71LL/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/S71LL/foodgram-project-react/actions/workflows/main.yml)
