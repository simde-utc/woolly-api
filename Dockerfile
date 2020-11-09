FROM python:3.8-slim-buster AS base

# TODO Change user

FROM base AS dependencies

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY Pipfile Pipfile.lock ./
RUN pip install -U pipenv && pipenv install --system

FROM dependencies AS app

WORKDIR /app
COPY . .

EXPOSE 8000
CMD python manage.py runserver 0.0.0.0:8000
