FROM node:22-slim AS node

FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV DOCKER_APP_DIRECTORY=/usr/src/app
ENV WEB_LIBRARY=/usr/src/app/distribution
ENV WEB_LIBRARY_BASE=/usr/src/app/static
ENV WEB_LIBRARY_SERV_DIR=${WEB_LIBRARY_BASE}/dist

FROM base AS builder

WORKDIR ${DOCKER_APP_DIRECTORY}

COPY ./ ${DOCKER_APP_DIRECTORY}/

COPY --from=node /usr/local /usr/local

# hadolint ignore=DL3003,DL3018
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    cmake \
    curl \
    gettext \
    git \
    libcairo2 \
    libcairo2-dev \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    libluajit-5.1-dev \
    libncurses-dev \
    libpq-dev \
    libreadline-dev \
    libtool \
    libuv1-dev \
    lua5.3 \
    pkg-config \
    unzip \
    zlib1g-dev \
    tree-sitter-cli \
	&& pip install --no-cache-dir poetry poetry-plugin-export \
	&& poetry export --with dev --without-hashes -f requirements.txt > Requirements.txt \
	&& pip install --no-cache-dir -r Requirements.txt 

RUN npm install \
	&& npm run build \
	&& mv ${WEB_LIBRARY_SERV_DIR} ${WEB_LIBRARY} 


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

RUN groupadd -g 1000 django\
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash django

COPY --from=node /usr/local /usr/local

# hadolint ignore=DL3003,DL3018
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    libcairo2 \
    libpq5 \
    libuv1 \
    libncurses6 \
    libreadline8 \
    luajit \
    tree-sitter-cli \
    xclip \
    && rm -rf /var/lib/apt/lists/* 



COPY --from=builder ${DOCKER_APP_DIRECTORY} ${DOCKER_APP_DIRECTORY}

COPY --from=builder /usr/local/bin/nvim /usr/local/bin/nvim
COPY --from=builder /usr/local/share/nvim /usr/local/share/nvim

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

COPY --from=builder ${DOCKER_APP_DIRECTORY} ${DOCKER_APP_DIRECTORY}
COPY --from=builder /usr/local/bin/nvim /usr/local/bin/nvim
COPY --from=builder /usr/local/share/nvim /usr/local/share/nvim
COPY --chown=django:django --from=builder /tmp/nvim-parser/python.so /home/django/.local/share/nvim/site/parser/python.so
COPY --chown=django:django --from=builder /tmp/nvim-parser/typescript.so /home/django/.local/share/nvim/site/parser/typescript.so

COPY --chown=django:django docker/ddionrails/entrypoint.sh ${DOCKER_APP_DIRECTORY}/

RUN mkdir /var/ddi_studies
RUN mkdir /var/model_cache
RUN mkdir -p /var/lib/ddionrails/backup/

RUN chown -R django:django /var/ddi_studies /var/model_cache /home/django/.local /var/lib/ddionrails/backup/

RUN chown -R django:django ${WEB_LIBRARY_BASE}

ENTRYPOINT [ "bash", "/usr/src/app/entrypoint.sh" ]
