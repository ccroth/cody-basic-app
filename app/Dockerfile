# syntax=docker/dockerfile:1

FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY app.py app.py
COPY gunicorn_config.py gunicorn_config.py
ADD templates /app/templates/
ADD static/css /app/static/css/

CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]