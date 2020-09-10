#!/bin/bash
set -e

python manage.py makemigrations
python manage.py migrate
python manage.py loaddata files/db.json

exec "$@"