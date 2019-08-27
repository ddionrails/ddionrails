FROM python:3.7.4-slim-stretch

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Hard coded again in entrypoint
ENV DOCKER_APP_DIRECTORY /usr/src/app

WORKDIR ${DOCKER_APP_DIRECTORY}

COPY ./ ${DOCKER_APP_DIRECTORY}/

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash-completion=1:2.1-4.3 \
        build-essential=12.3 \
        curl=7.52.1-5+deb9u9 \
        git=1:2.11.0-3+deb9u4 \
        graphviz=2.38.0-17 \
        graphviz-dev=2.38.0-17 \
        netcat=1.10-41 \
        openssh-client=1:7.4p1-10+deb9u6 \
        python-psycopg2=2.6.2-1 \
        vim-tiny=2:8.0.0197-4+deb9u3 \
    && curl -sL https://deb.nodesource.com/setup_12.x | bash - \
    && apt-get install -y --no-install-recommends nodejs=12.* \
    && npm install \
    && npm run build \
    && rm -rf ./node_modules/ \
    && rm -rf /var/lib/apt/lists/* 

# hadolint ignore=DL3013
RUN pip install --upgrade pipenv
# It turned out to be easier to work with the dev dependencies in a venv
RUN pipenv install --dev --system

WORKDIR ${DOCKER_APP_DIRECTORY}

# Set up entrypoint
COPY ./docker/ddionrails/dev/entrypoint.sh ${DOCKER_APP_DIRECTORY}/

# Some dev creature comforts for bash work
COPY ./docker/ddionrails/dev/dev.bashrc /root/.bashrc

ENTRYPOINT [ "bash", "/usr/src/app/entrypoint.sh" ]
