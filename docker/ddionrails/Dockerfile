FROM python:3.13-alpine3.20

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Hard coded again in entrypoint
ENV DOCKER_APP_DIRECTORY /usr/src/app
ENV WEB_LIBRARY /usr/src/app/distribution
ENV WEB_LIBRARY_SERV_DIR /usr/src/app/static/dist

WORKDIR ${DOCKER_APP_DIRECTORY}

COPY ./ ${DOCKER_APP_DIRECTORY}/

# hadolint ignore=DL3003,DL3018
RUN apk add --no-cache \
    bash \
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
    && npm install \
    && npm run build \
    && apk del nodejs npm \
    && rm -rf /var/cache/apk/* \
    && rm -rf node_modules \
    && mv ${WEB_LIBRARY_SERV_DIR} ${WEB_LIBRARY}

# Set up entrypoint
COPY docker/ddionrails/entrypoint.sh ${DOCKER_APP_DIRECTORY}/

ENTRYPOINT [ "bash", "/usr/src/app/entrypoint.sh" ]
