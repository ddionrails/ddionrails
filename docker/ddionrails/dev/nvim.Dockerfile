FROM python:3.13-alpine3.23

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
	cairo \
	cairo-dev \
	freetype-dev \
	git \
	jpeg-dev \
	nodejs \
	npm \
	pkgconfig \
	postgresql-dev \
	ripgrep \
	zlib-dev \
	xclip \
	&& pip install --no-cache-dir poetry poetry-plugin-export \
	&& poetry export --with dev --without-hashes -f requirements.txt > Requirements.txt \
	&& pip install --no-cache-dir -r Requirements.txt \
	&& rm Requirements.txt \
	&& npm install \
	&& npm install -g typescript typescript-language-server jest ts-node \
	&& npm run build \
	&& rm -rf /var/cache/apk/* \
	&& mv ${WEB_LIBRARY_SERV_DIR} ${WEB_LIBRARY}

#RUN apk add --no-cache \
#	luarocks make git lua-dev \
#	&& ln -s /usr/bin/luarocks-5.1 /usr/bin/luarocks

RUN apk add --no-cache \
    git cmake build-base libtool \
    libstdc++ gettext curl unzip \
    lua5.3 luajit readline-dev ncurses-dev \
    libuv-dev \
    tree-sitter tree-sitter-dev pkgconfig

RUN git clone https://github.com/neovim/neovim.git  \
    && cd neovim \
    && git checkout v0.11.4  \
    && apk add --no-cache cmake \
    && make distclean \
    && make CMAKE_BUILD_TYPE=Release \
    && make install
    

RUN adduser -D -u 1000 -s /bin/bash dev

RUN git clone https://github.com/tree-sitter/tree-sitter-python.git \
    && cd tree-sitter-python \
    && cc -fPIC -O2 -shared src/parser.c src/scanner.c -o python.so \
    && mkdir -p /home/dev/.local/share/nvim/site/parser \
    && mv python.so /home/dev/.local/share/nvim/site/parser/ \
    && cd .. && rm -rf tree-sitter-python \
    && chown -R dev:dev /home/dev/.local

# Set up entrypoint
COPY docker/ddionrails/entrypoint.sh ${DOCKER_APP_DIRECTORY}/

ENTRYPOINT [ "bash", "/usr/src/app/entrypoint.sh" ]
