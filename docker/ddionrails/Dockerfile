FROM python:3.7.3-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV DOCKER_APP_DIRECTORY /usr/src/app

WORKDIR ${DOCKER_APP_DIRECTORY}

COPY ./ ${DOCKER_APP_DIRECTORY}/

RUN apk update \
    && apk add \
        bash \
        build-base \
        git \
        graphviz \
        graphviz-dev \
        nodejs \
        nodejs-npm \
        postgresql-dev \
        # pipenv did not want to build without these
        gcc \
        libffi-dev \
        make \
        musl-dev \
    && rm -rf /var/cache/apk/*

RUN pip install --upgrade pipenv
RUN pipenv install --system --dev
RUN npm install

# Setup frontend
RUN cd ./node_modules/ddionrails-elasticsearch \
    && npm install \
    && ./node_modules/.bin/ng build --prod
RUN ./node_modules/.bin/webpack --config webpack.config.js
ENTRYPOINT [ ${DOCKER_APP_DIRECTORY}"/entrypoint.sh" ]