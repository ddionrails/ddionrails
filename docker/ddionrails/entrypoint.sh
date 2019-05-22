#!/bin/bash
# Update static files if needed.
WEBPACK_STATS=webpack-stats.json
BUILD_DEPENDENCIES=$(ls ${WEBPACK_STATS})
LIVE_DEPENDENCIES=$(ls static/${WEBPACK_STATS})

echo "Check for old dependencies"
cmp "${BUILD_DEPENDENCIES}" "${LIVE_DEPENDENCIES}"
DEPENDENCY_DIFF=$?

if [ ${DEPENDENCY_DIFF} -gt 0 ]; then
    echo "Image dependencies have changed."
    echo "Overwriting old dependencies."
    ./node_modules/.bin/webpack --config webpack.config.js
    cp ${BUILD_DEPENDENCIES} ${LIVE_DEPENDENCIES}
fi

# The Database container may not be there yet
echo "Waiting for Database"

if [ -z "${POSTGRES_HOST}" ]; then
    echo "Error: POSTGRES_HOST is not set"
    exit 0
fi

if [ -z "${POSTGRES_PORT}" ]; then
    echo "Error: POSTGRES_PORT is not set"
    exit 0
fi

while ! nc -z "${POSTGRES_HOST}" "${POSTGRES_PORT}"; do
    sleep 0.1
done

echo "Database started"


# Collect Admin stiling etc.
python manage.py collectstatic --noinput

echo "Initialising System"
python manage.py system || echo "Initialising System failed."

echo "Running migrations."
python manage.py migrate && \
echo "Starting rqworker" && \
python manage.py rqworker &

echo "Starting server"
exec "$@"

