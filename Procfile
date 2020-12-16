release: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py clearsessions
web: gunicorn bourseLibre.wsgi --log-file -
