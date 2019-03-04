release: python manage.py makemigrations && python manage.py migrate   && manage.py migrate auth && manage.py migrate --run-syncdb
web: gunicorn bourseLibre.wsgi --log-file -
