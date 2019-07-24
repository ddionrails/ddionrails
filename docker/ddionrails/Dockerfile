FROM python:3.7.4-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Hard coded again in entrypoint
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
    && rm -rf /var/cache/apk/*

# install the latest version of pipenv
# hadolint ignore=DL3013
RUN pip install --upgrade pipenv
RUN pipenv install --system --dev
RUN npm install

# Collect all files to serve as static files
RUN cd ./node_modules/ddionrails-elasticsearch \
    && npm install \
    && ./node_modules/.bin/ng build --prod
# Use webpack to bundle static files
RUN npm run build

# Set up entrypoint
RUN mv docker/ddionrails/entrypoint.sh ${DOCKER_APP_DIRECTORY}/

ENTRYPOINT [ "bash", "/usr/src/app/entrypoint.sh" ]
