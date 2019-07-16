#!/bin/bash
# Update static files if needed.
WEBPACK_STATS=webpack-stats.json
BUILD_DEPENDENCIES=/usr/src/app/${WEBPACK_STATS}
LIVE_DEPENDENCIES=/usr/src/app/static/${WEBPACK_STATS}

echo "Check for old dependencies"
cmp "${BUILD_DEPENDENCIES}" "${LIVE_DEPENDENCIES}"
DEPENDENCY_DIFF=$?

if [ "${DEPENDENCY_DIFF}" -gt 0 ] || [ ! -f "${LIVE_DEPENDENCIES}" ]; then
    echo "Image dependencies have changed."
    echo "Overwriting old dependencies."
    rm -rf /usr/src/app/static/dist/*
    npm run build
    cp ${BUILD_DEPENDENCIES} ${LIVE_DEPENDENCIES}
fi


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

