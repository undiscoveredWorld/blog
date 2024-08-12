# Blog
Symple realisation of blog backend-side system.  

# Getting start

> In any case you need create two env files in root of project
> 1. '.env'. Example filling:
>   ```
>   SECRET_KEY={your secret key}
>   ```
> 2. 'docker.env'. Example filling:
>   ```
>   POSTGRES_PASSWORD=<Password>
>   POSTGRES_USER=<USERNAME>
>   POSTGRES_DB=<DB_NAME>
>   ```

## Native(without `make` or `docker`)
- Firstly create virtual environment
- Next you need install requirements via command
    ```shell
    python -m pip install -r requirements.txt
    ```
- Run postgres if you didn't do it
- Then do migration with these commands:
    ```shell
    python manage.py makemigrations
    python manage.py sqlmigrate Auth 0001
    python manage.py sqlmigrate Posts 0001
    python manage.py migrate Auth 0001
    python manage.py migrate Posts 0001
    ```
- Create superuser via command
  ```shell
  python manage.py createsuperuser 
  ```
- Run django server via command
    ```shell
    python manage.py runserver
    ```

# Docker
- Build docker image via `docker build .`
- Run postgres if you didn't do it
- Create superuser via command
  ```shell
  python manage.py createsuperuser 
  ```
- Run built docker image with command:
  ```shell
	docker run -p 8080:8080 -d --rm <Image name>
  ```

# Make
- Run command `make first run`
- In all next cases use `make run`

> If you need docker, run `make build-and-run-docker`