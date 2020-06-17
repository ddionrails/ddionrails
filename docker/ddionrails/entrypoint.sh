#!/bin/bash
# Collect Admin stiling etc.
python manage.py collectstatic --noinput

echo "Initialising System"
python manage.py system || echo "Initialising System failed." &

echo "Running migrations."
python manage.py migrate && \
echo "Starting rqworker" && \
python manage.py rqworker &

echo "Creating search indices"
python manage.py search_index --create || echo "Creating search indices failed." &

apk add --no-cache npm && \
npm install && \
npm run build && \
rm -r node_modules && \
apk del npm &

echo "Starting server"
exec "$@"

