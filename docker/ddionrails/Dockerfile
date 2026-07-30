FROM python:3.13-alpine3.20 AS base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV DOCKER_APP_DIRECTORY /usr/src/app
ENV WEB_LIBRARY /usr/src/app/distribution
ENV WEB_LIBRARY_SERV_DIR /usr/src/app/static/dist

FROM base AS builder

WORKDIR ${DOCKER_APP_DIRECTORY}

COPY ./ ${DOCKER_APP_DIRECTORY}/

# hadolint ignore=DL3003,DL3018
RUN apk add --no-cache \
    build-base \
    git \
    jpeg-dev \
    nodejs \
    npm \
    postgresql-dev \
    zlib-dev \
    freetype-dev \
    pkgconfig cairo-dev cairo \
    && pip install --no-cache-dir --upgrade poetry poetry-plugin-export \
    && poetry export --without-hashes -f requirements.txt > Requirements.txt \
    && pip install --no-cache-dir -r Requirements.txt \
    && pip uninstall -y poetry \
    && rm Requirements.txt \
    && npm ci \
    && npm run build \
    && rm -rf node_modules \
    && mv ${WEB_LIBRARY_SERV_DIR} ${WEB_LIBRARY}

FROM base

WORKDIR ${DOCKER_APP_DIRECTORY}

RUN addgroup -g 1000 -S django && \
    adduser -u 1000 -G django -s /bin/bash -D django

RUN apk add --no-cache \
    bash \
    cairo \
    postgresql-libs \
    && rm -rf /var/cache/apk/*

COPY --from=builder ${DOCKER_APP_DIRECTORY} ${DOCKER_APP_DIRECTORY}
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

RUN chown -R django:django /usr/src/app/docker/ddionrails/entrypoint.sh

USER django

ENTRYPOINT [ "bash", "/usr/src/app/docker/ddionrails/entrypoint.sh" ]
