release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn bourseLibre.wsgi --log-file -
