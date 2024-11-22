FROM python:3.12-alpine3.20

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
	&& pip install --no-cache-dir --upgrade pipfile-requirements==0.3.0 \
	&& pip install --no-cache-dir --upgrade chardet==4.0.0 \
	&& pipfile2req Pipfile.lock > Requirements.txt \
	&& pip install --no-cache-dir -r Requirements.txt \
	&& pip uninstall -y pipfile-requirements \
	&& rm Requirements.txt \
	&& npm install \
	&& npm run build \
	&& apk del nodejs npm \
	&& rm -rf /var/cache/apk/* \
	&& rm -rf node_modules \
	&& mv ${WEB_LIBRARY_SERV_DIR} ${WEB_LIBRARY}

RUN apk add --no-cache \
	neovim luarocks make git lua-dev \
	&& ln -s /usr/bin/luarocks-5.1 /usr/bin/luarocks

RUN adduser -D -u 1000 -s /bin/bash dev


# Set up entrypoint
COPY docker/ddionrails/entrypoint.sh ${DOCKER_APP_DIRECTORY}/

ENTRYPOINT [ "bash", "/usr/src/app/entrypoint.sh" ]
