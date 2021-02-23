#!/bin/bash
source ~/.bashrc
source ~/permacat/permacatenv/bin/activate

python ~/permacat/manage.py envoiMails -env=bourseLIbre.settings.production
