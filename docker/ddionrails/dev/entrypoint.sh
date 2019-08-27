#!/bin/bash
# Update static files if needed.
WEBPACK_STATS=webpack-stats.json
BUILD_DEPENDENCIES=/usr/src/app/${WEBPACK_STATS}
LIVE_DEPENDENCIES=/usr/src/app/static/${WEBPACK_STATS}

echo "Check for old dependencies"
cmp "${BUILD_DEPENDENCIES}" "${LIVE_DEPENDENCIES}"
DEPENDENCY_DIFF=$?

if [ "${DEPENDENCY_DIFF}" -gt 0 ] || [ ! -f "${LIVE_DEPENDENCIES}" ] || [ ! -f "${BUILD_DEPENDENCIES}" ]; then
    echo "Image dependencies have changed."
    echo "Overwriting old dependencies."
    rm -rf /usr/src/app/static/dist/*
    npm install
    cd /usr/src/app
    npm run build
    cp ${BUILD_DEPENDENCIES} ${LIVE_DEPENDENCIES}
fi

# Install pre-commit hooks
pre-commit install
nohup pre-commit install-hooks > /dev/null 2>&1 & 
nohup pre-commit install -t pre-push > /dev/null 2>&1 &


# Collect Admin styling etc.
python manage.py collectstatic --noinput

echo "Initializing System"
python manage.py system || echo "Initializing System failed." &

echo "Running migrations."
python manage.py migrate && \
echo "Starting rqworker" && \
python manage.py rqworker &

echo "Creating search indices"
python manage.py search_index --create || echo "Creating search indices failed." &

echo "Starting server"
exec "$@"

