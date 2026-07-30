FROM python:3.13-alpine3.23 AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV DOCKER_APP_DIRECTORY=/usr/src/app
ENV WEB_LIBRARY=/usr/src/app/distribution
ENV WEB_LIBRARY_SERV_DIR=/usr/src/app/static/dist

FROM base AS builder

WORKDIR ${DOCKER_APP_DIRECTORY}

COPY ./ ${DOCKER_APP_DIRECTORY}/

# hadolint ignore=DL3003,DL3018
RUN apk add --no-cache \
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
	zlib-dev \
	&& pip install --no-cache-dir poetry poetry-plugin-export \
	&& poetry export --with dev --without-hashes -f requirements.txt > Requirements.txt \
	&& pip install --no-cache-dir -r Requirements.txt \
	&& rm Requirements.txt \
	&& npm install \
	&& npm run build \
	&& rm -rf /var/cache/apk/* \
	&& mv ${WEB_LIBRARY_SERV_DIR} ${WEB_LIBRARY}

# hadolint ignore=DL3003,DL3018
RUN apk add --no-cache \
    git cmake build-base libtool \
    gettext curl unzip \
    lua5.3 luajit \
    readline-dev ncurses-dev libuv-dev \
    tree-sitter tree-sitter-dev pkgconfig

RUN git clone https://github.com/neovim/neovim.git /tmp/neovim \
    && cd /tmp/neovim \
    && git checkout v0.12.0 \
    && make distclean \
    && make CMAKE_BUILD_TYPE=Release \
    && make install \
    && rm -rf /tmp/neovim

RUN git clone --depth 1 https://github.com/tree-sitter/tree-sitter-python.git /tmp/tree-sitter-python \
    && cd /tmp/tree-sitter-python \
    && cc -fPIC -O2 -shared src/parser.c src/scanner.c -o python.so \
    && mkdir -p /tmp/nvim-parser \
    && mv python.so /tmp/nvim-parser/ \
    && rm -rf /tmp/tree-sitter-python

RUN mkdir -p ~/.local/share/nvim/site/parser \
    && git clone --depth 1 https://github.com/tree-sitter/tree-sitter-typescript.git /tmp/tree-sitter-typescript \
    && cd /tmp/tree-sitter-typescript/typescript \
    && cc -shared -fPIC -o typescript.so src/parser.c src/scanner.c -Isrc \
    && mv typescript.so /tmp/nvim-parser/ \
    && rm -rf /tmp/tree-sitter-typescript


FROM base

WORKDIR ${DOCKER_APP_DIRECTORY}

RUN addgroup -g 1000 -S dev && \
    adduser -u 1000 -G dev -s /bin/bash -D dev

RUN apk add --no-cache \
    bash \
    cairo \
    curl \
    git \
    nodejs \
    npm \
    postgresql-libs \
    ripgrep \
    xclip \
    gettext \
    libstdc++ \
    luajit \
    ncurses \
    libuv \
    readline \
    tree-sitter tree-sitter-dev pkgconfig \
    && npm install -g typescript typescript-language-server jest ts-node tree-sitter

COPY --from=builder ${DOCKER_APP_DIRECTORY} ${DOCKER_APP_DIRECTORY}
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin/nvim /usr/local/bin/nvim
COPY --from=builder /usr/local/share/nvim /usr/local/share/nvim
COPY --chown=dev:dev --from=builder /tmp/nvim-parser/python.so /home/dev/.local/share/nvim/site/parser/python.so
COPY --chown=dev:dev --from=builder /tmp/nvim-parser/typescript.so /home/dev/.local/share/nvim/site/parser/typescript.so

COPY --chown=dev:dev docker/ddionrails/entrypoint.sh ${DOCKER_APP_DIRECTORY}/

RUN mkdir /var/ddi_studies

RUN chown -R dev:dev /var/ddi_studies /home/dev/.local

USER dev

ENTRYPOINT [ "bash", "/usr/src/app/entrypoint.sh" ]
