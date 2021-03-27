#!/bin/bash
set -e

python manage.py makemigrations master accounts
python manage.py migrate --fake-initial
python manage.py loaddata files/db.json

exec "$@"