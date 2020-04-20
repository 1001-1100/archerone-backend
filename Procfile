release: python manage.py makemigrations api && python manage.py migrate api --no-input && python manage.py makemigrations && python manage.py migrate --no-input
web: gunicorn backend.wsgi
