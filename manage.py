#!/usr/bin/env python
import os
import sys
#
#source /home/tchenrezi/Django/venv3.6/bin/activate

#/home/tchenrezi/Django/venv3.6/bin/python /PycharmProjects/mercatLliure/manage.py migrate --run-syncdb
#./manage.py clear_index
#./manage.py update_index
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bourseLibre.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
