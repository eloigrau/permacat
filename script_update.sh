#!/bin/bash
cd /home/udjango/permacat
git pull
source /home/udjango/permacat/permacatenv/bin/activate
python manage.py migrate --settings=bourseLibre.settings.production
supervisorctl restart permacat_supervisor

