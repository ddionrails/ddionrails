FROM python:3.7.3-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

RUN apk update \
    && apk add git build-base \
    && apk add bash \
    && apk add graphviz graphviz-dev \
    && apk add postgresql-dev \
    && apk add nodejs nodejs-npm

RUN pip install --upgrade pipenv
COPY ./Pipfile /usr/src/app/Pipfile
RUN pipenv install --skip-lock --system --dev
COPY ./package.json /usr/src/app/package.json
RUN npm install

COPY . /usr/src/app/