FROM python:3.7.3-slim-stretch

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Hard coded again in entrypoint
ENV DOCKER_APP_DIRECTORY /usr/src/app

WORKDIR ${DOCKER_APP_DIRECTORY}

COPY ./ ${DOCKER_APP_DIRECTORY}/

RUN  apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential=12.3 \
        git=1:2.11.0-3+deb9u4 \
        graphviz=2.38.0-17 \
        graphviz-dev=2.38.0-17 \
        curl=7.52.1-5+deb9u9 \
        python-psycopg2=2.6.2-1 \
        netcat=1.10-41 \
    && curl -sL https://deb.nodesource.com/setup_12.x | bash - \
    && apt-get install -y --no-install-recommends nodejs=12.6.0-1nodesource1 \
    && rm -rf /var/lib/apt/lists/* 

# install the latest version of pipenv
# hadolint ignore=DL3013
RUN pip install --upgrade pipenv
RUN pipenv install --system --dev
RUN npm install

# Collect all files to serve as static files
WORKDIR ${DOCKER_APP_DIRECTORY}/node_modules/ddionrails-elasticsearch
RUN npm install \
    && ./node_modules/.bin/ng build --prod

WORKDIR ${DOCKER_APP_DIRECTORY}

# Use webpack to bundle static files
RUN npm run build

# Set up entrypoint
RUN mv docker/ddionrails/entrypoint.sh ${DOCKER_APP_DIRECTORY}/

ENTRYPOINT [ "bash", "/usr/src/app/entrypoint.sh" ]
