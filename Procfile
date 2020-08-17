release: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runcrons
web: gunicorn bourseLibre.wsgi --log-file -
