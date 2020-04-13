release: python manage.py makemigrations &&  python manage.py migrate --fake --no-input
web: gunicorn backend.wsgi
