#!/bin/bash
set -e

python manage.py makemigrations master accounts
python manage.py migrate
python manage.py loaddata files/db.json

exec "$@"