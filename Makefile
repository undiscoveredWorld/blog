run-postgres:
	docker run --name blog_postgres --rm --env-file docker.env -d -p 5432:5432 postgres:alpine