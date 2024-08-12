run-postgres:
	docker run --name blog_postgres --rm \
		--env-file docker.env -d -p 5432:5432 postgres:alpine

first-run:
	make run-postgres
	python manage.py makemigrations
	python manage.py sqlmigrate Auth 0001
	python manage.py sqlmigrate Post 0001
	python manage.py migrate Auth 0001
	python manage.py migrate Post 0001
	python manage.py runserver

run:
	make run-postgres
	python manage.py runserver

build-and-run-docker:
	docker build -t blog .
	make run-postgres
	docker run -p 8080:8080 -d --rm \
		--link blog_postgres \
		-e POSTGRES_HOST=blog_postgres \
		blog
