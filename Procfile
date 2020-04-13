release: python manage.py makemigrations &&  python manage.py migrate --no-input
web: gunicorn backend.wsgi
