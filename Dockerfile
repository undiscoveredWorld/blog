FROM python:3.11.9-alpine3.20

WORKDIR /app/Blog

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
CMD sh run.bash
