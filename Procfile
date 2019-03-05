release: python manage.py migrate --run-syncdb --all
web: gunicorn bourseLibre.wsgi --log-file -
