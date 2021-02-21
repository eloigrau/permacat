#!/bin/bash

cd /home/udjango/permacat
git pull
source permacatenv/bin/activate
sudo supervisorctl restart permacat_supervisor
export DJANGO_SETTINGS_MODULE=bourseLibre.settings.production
python manage.py runcrons

