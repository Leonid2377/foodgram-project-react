# Проект продуктовый помощник
IP 84.201.142.74 (на стадии доработки)
![example workflow](https://github.com/Leonid2377/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
# yamdb_final
#Описание проекта
Проект позволяет зарегистрироваться пользователям
и оставлять отзывы на различные произведения

**Как пользоватся**:
>Скопировать проект командой: 
>> `git clone git@github.com:Leonid2377/yamdb_final.git`

## Для запуска на сервере ubuntu:
>В директории infra нужно создать файл .env и заполнить данными:
  ```
  `DB_ENGINE=django.db.backends.postgresql`
  `DB_NAME=postgres`
  `POSTGRES_USER=postgres`
  `POSTGRES_PASSWORD= # установите свой пароль`
  `DB_HOST=db`
  `DB_PORT=5432`
  ```

>Запустить из директории infra:
  ```
  sudo docker-compose up -d --build
  ```
  
  ```
  sudo docker-compose exec backend python manage.py migrate --noinput
  ```
  
  ```
  docker-compose exec web python manage.py createsuperuser`
  ```
  
  ```
  docker-compose exec web python manage.py collectstatic --no-input`
  ```

> остановить проект: `docker-compose down -v`

*проект запустится по ip вашего сервера

**Автор проекта: Старостин Леонид** 
