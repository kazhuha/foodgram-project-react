# FOODGRAM
## Социальная сеть для блогеров

![example workflow](https://github.com/kazhuha/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Технологии

При разработке использован следущий стек технологий:

- Python 3.7
- Django 2.2.19
- Django Rest Framework
- Simple-GWT
- PstgreSQL

## Установка


Сконируйте репозиторий выполнив команду:

```sh
git clone <ссылка на репозиторий>
```

В  папке infrs проекта создайте файл .env с переменными окружения для работы с базой данных. Укажите следующие параметры:

```sh
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=username # логин для подключения к базе данных
POSTGRES_PASSWORD=password # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
SECRET_KEY=supersecretkey # (установите свой)
```

## Docker

Запустите контейнеры web(отвечает за приложение), nginx(сервер) и db(база данных) выполнением команды:
```sh
docker-compose up -d --build
```
Для проверки работы контейнеров выполните команду:
```sh
docker container ls
```

Выполните по очереди команды:

```sh
docker-compose exec <название котнейнера web приложения> python manage.py migrate
docker-compose exec <название котнейнера web приложения> python manage.py createsuperuser
docker-compose exec <название котнейнера web приложения> python manage.py collectstatic --no-input
```
Для заполнения базы данных тестовыми данными выполните команду:
```sh
docker-compose exec <название котнейнера web приложения> python manage.py load_data_csv
```



* ##### Проверьте работоспособность [приложения](http://localhost/ "Title").
* ##### Протестируйте приложение, например, через Postman. Примеры команд описаны в [redoc](http://localhost/api/docs/redoc.html# "Title").


Разрабатывали проект:
* Кожушкевич Александр - https://github.com/kazhuha
* Готовый проект можно проверить по [ссылке](http://receptorium.ddns.net/ "Title").
