FROM python:3.8.0-alpine3.10

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
    && pip install --no-cache-dir --upgrade pipfile-requirements==0.1.0.post0 \
    && pipfile2req Pipfile.lock > Requirements.txt \
    && pip install --no-cache-dir -r Requirements.txt \
    && pip uninstall -y pipfile-requirements \
    && rm Requirements.txt \
    && npm install \
    && npm run build \
    && apk del nodejs nodejs-npm \
    && rm -rf /var/cache/apk/* \
    && rm -rf node_modules 

# Set up entrypoint
COPY docker/ddionrails/entrypoint.sh ${DOCKER_APP_DIRECTORY}/

ENTRYPOINT [ "bash", "/usr/src/app/entrypoint.sh" ]
