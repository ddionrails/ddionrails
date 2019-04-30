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

python manage.py migrate && \
echo "Starting rqworker" && \
python manage.py rqworker & 

echo "Starting server"
exec "$@"
