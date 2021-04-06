#!/bin/bash
cd /home/udjango/permacat
git pull
source /home/udjango/permacat/permacatenv/bin/activate
python manage.py migrate --settings=bourseLibre.settings.production
python manage.py collectstatic --noinput
python manage.py crontab add
pip install -r requirements.txt
sudo systemctl restart nginx
sudo supervisorctl restart permacat_supervisor

