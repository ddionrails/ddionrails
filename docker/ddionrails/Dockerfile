FROM python:3.7.4-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Hard coded again in entrypoint
ENV DOCKER_APP_DIRECTORY /usr/src/app

WORKDIR ${DOCKER_APP_DIRECTORY}

COPY ./ ${DOCKER_APP_DIRECTORY}/

# hadolint ignore=DL3003,DL3018
RUN apk add --no-cache \
        bash \
        build-base \
        git \
        jpeg-dev \
        nodejs \
        nodejs-npm \
        postgresql-dev \
        zlib-dev \
    && pip install --upgrade pipenv \
    && pipenv install --system --ignore-pipfile \
    && npm install \
    && npm run build \
    && apk del nodejs nodejs-npm \
    && pip uninstall -y pipenv \
    && rm -rf /var/cache/apk/* \
    && rm -rf node_modules 

# Set up entrypoint
COPY docker/ddionrails/entrypoint.sh ${DOCKER_APP_DIRECTORY}/

ENTRYPOINT [ "bash", "/usr/src/app/entrypoint.sh" ]
