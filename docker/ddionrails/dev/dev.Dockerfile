FROM python:3.10.0b3-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Hard coded again in entrypoint
ENV DOCKER_APP_DIRECTORY /usr/src/app

WORKDIR ${DOCKER_APP_DIRECTORY}

COPY ./ ${DOCKER_APP_DIRECTORY}/

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    bash-completion>=1:2 \
    build-essential>=12.3 \
    curl>=7 \
    git>=1:2 \
    graphviz>=2.38 \
    graphviz-dev>=2.38 \
    netcat>=1 \
    openssh-client>=1:7 \
    python-psycopg2>=2 \
    libpq-dev>=11.5 \
    gcc>=4:8 \
    libjpeg-dev>=1:1.5 \
    zlib1g-dev>=1:1.2 \
    vim-tiny>=2:8 \
    && pip install --no-cache-dir --upgrade pipfile-requirements==0.1.0.post0 \
    && pipfile2req Pipfile.lock > Requirements.txt \
    && pipfile2req --dev Pipfile.lock >> Requirements.txt \
    && pip install --no-cache-dir -r Requirements.txt \
    && rm Requirements.txt \
    && curl -sL https://deb.nodesource.com/setup_12.x | bash - \
    && apt-get install -y --no-install-recommends nodejs=12.* \
    && npm install \
    && npm run build \
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
