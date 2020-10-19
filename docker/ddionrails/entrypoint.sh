#!/bin/bash
# Collect Admin stiling etc.
mv ${WEB_LIBRARY}/* ${WEB_LIBRARY_SERV_DIR}/
python manage.py collectstatic --noinput

echo "Initialising System"
python manage.py system || echo "Initialising System failed." &

echo "Running migrations."
python manage.py migrate && \
echo "Starting rqworker" && \
python manage.py rqworker &

echo "Creating search indices"
python manage.py search_index --create || echo "Creating search indices failed." &

echo "Starting server"
exec "$@"

