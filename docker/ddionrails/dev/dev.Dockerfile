FROM python:3.12-slim-bullseye


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Hard coded again in entrypoint
ENV DOCKER_APP_DIRECTORY /usr/src/app

WORKDIR ${DOCKER_APP_DIRECTORY}

COPY ./ ${DOCKER_APP_DIRECTORY}/

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    bash-completion>=1:2.8-6 \
    build-essential>=12.6 \
    curl>=7.64.0-4+deb10u2 \
    git>=1:2 \
    graphviz>=2.38 \
    graphviz-dev>=2.38 \
    netcat>=1 \
    openssh-client>=1:7 \
    libpq-dev>=11.5 \
    pkg-config libcairo2-dev libjpeg-dev libgif-dev \
    gcc>=4:8 \
    libjpeg-dev>=1:1.5 \
    zlib1g-dev>=1:1.2 \
    libfreetype6-dev>=2.9.1-3+deb10u2 \
    vim-tiny>=2:8 \
    && pip install --no-cache-dir --upgrade poetry\
    && poetry export --with dev --without-hashes -f requirements.txt > Requirements.txt \
    && pip install --no-cache-dir -r Requirements.txt \
    && rm Requirements.txt \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get install -y --no-install-recommends npm \
    && npm install \
    && npm run build \
    && npm install -g jest ts-node \
    && pip uninstall -y --no-input pipenv \
    && rm -rf ./node_modules/ \
    && rm -rf /var/lib/apt/lists/* 

# hadolint ignore=DL3013
RUN pip install --upgrade pipenv
# It turned out to be easier to work with the dev dependencies in a venv

WORKDIR ${DOCKER_APP_DIRECTORY}

# Set up entrypoint
COPY ./docker/ddionrails/dev/entrypoint.sh ${DOCKER_APP_DIRECTORY}/

# Some dev creature comforts for bash work
COPY ./docker/ddionrails/dev/dev.bashrc /root/.bashrc

ENTRYPOINT [ "bash", "/usr/src/app/entrypoint.sh" ]
