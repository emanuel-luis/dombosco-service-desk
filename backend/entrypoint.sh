#!/bin/sh

echo "Waiting for database..."

while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
  sleep 0.1
done

echo "Database started"

python manage.py flush --no-input
python manage.py migrate

exec "$@"
