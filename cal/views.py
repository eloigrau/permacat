# cal/views.py

from datetime import datetime,  timedelta
from django.views import generic
from django.utils.safestring import mark_safe

from blog.models import Article
from .utils import Calendar
from django.shortcuts import render
from calendar import monthrange


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return datetime(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'mois=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'mois=' + str(next_month.year) + '-' + str(next_month.month)
    return month

def agenda(request):
    # use today's date for the calendar
    if not 'mois' in request.GET:
        d = get_date(request.GET.get('day', None))
    else:
        d = get_date(request.GET.get('mois', None))

    # Instantiate our calendar class with today's year and date
    cal = Calendar(d.year, d.month)

    # Call the formatmonth method, which returns our calendar as a table
    html_cal = mark_safe(cal.formatmonth(request, withyear=True))
    return render(request, 'calendrier.html', {'calendar':html_cal, 'annee':d.year, 'mois':cal.formatmonthname(d.year, d.month, withyear=False, width=10), 'prev_month':prev_month(d), 'next_month':next_month(d)})
