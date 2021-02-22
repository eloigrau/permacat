#!/bin/bash

cd /home/udjango/permacat
git pull
source /home/udjango/permacat/permacatenv/bin/activate
sudo supervisorctl restart permacat_supervisor
export DJANGO_SETTINGS_MODULE=bourseLibre.settings.production
python manage.py migrate
python manage.py runcrons

