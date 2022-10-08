FROM python:3.10.5-slim-buster as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install  dependencies
RUN apt update \
    && apt install gcc musl-dev -y

# install dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

FROM python:3.10.5-slim-buster

RUN mkdir -p /home/app

RUN addgroup --system --gid 1002 app && adduser --system --uid 1002 --gid 1002 app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
ENV DJANGO_SUPERUSER_PASSWORD=admin
ENV DJANGO_SUPERUSER_USERNAME=admin
ENV DJANGO_SUPERUSER_ROLE=1
ENV DJANGO_SUPERUSER_EMAIL=admin@admin.com
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install dependencies
RUN apt update && apt install netcat -y
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app
EXPOSE 8000

RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py createsuperuser --noinput

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "CommunerProject.wsgi:application"]