#!/bin/bash
cd /home/udjango/permacat
git pull
source /home/udjango/permacat/permacatenv/bin/activate
sudo supervisorctl restart permacat_supervisor
python manage.py migrate --settings=bourseLibre.settings.production
#python manage.py runcrons --settings=bourseLibre.settings.production

