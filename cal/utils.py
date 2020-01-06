# cal/utils.py

from datetime import datetime, timedelta
from calendar import LocaleHTMLCalendar
from blog.models import Article, Projet
from ateliers.models import Atelier
from django.db.models import Q
import random

class Calendar(LocaleHTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        self.now = datetime.now
        super(Calendar, self).__init__()


    # formats a day as a td
    # filter events by day
    def formatday(self, day, events_arti, events_proj, events_per_day_atel):
        events_per_day_arti = events_arti.filter(Q(start_time__day=day) | Q(start_time__day__lt=day, end_time__day__gte=day))
        events_per_day_proj = events_proj.filter(Q(start_time__day=day) | Q(start_time__day__lt=day, end_time__day__gte=day))
        events_per_day_atel = events_proj.filter(Q(start_time__day=day) | Q(start_time__day__lt=day, end_time__day__gte=day))

        d = ''
        for event in events_per_day_arti:
            titre = event.titre if len(event.titre)<30 else event.titre[:27] + "..."
            d += "<li style=''> <a href='"+event.get_absolute_url() +"'>"+titre+'</a> </li>'
        for event in events_per_day_proj:
            titre = event.titre if len(event.titre)<30 else event.titre[:27] + "..."
            d += "<li style=''> <a href='"+event.get_absolute_url() +"'>"+titre+'</a> </li>'

        now = datetime.now()
        if now.year > self.year or (now.year == self.year and now.month > self.month) :
            style = "style='background-color:darkgrey'"
        elif now.year == self.year and now.month == self.month and now.day > day:
            style = "style='background-color:grey'"
        elif now.year == self.year and now.month == self.month and now.day == day:
            style = "style='background-color:#66ff66'"
        else:
            style = "style='background-color:#ccffcc'"

        if day != 0:
                return "<td "+style+"><span class='date'>"+str(day)+'</span><ul class="ul_calendar">'+str(d)+' </ul></td>'

        return "<td '></td>"

    # formats a week as a tr
    def formatweek(self, theweek, events_arti, events_proj, events_per_day_atel):
        week = ''

        for d, weekday in theweek:
            week += self.formatday(d, events_arti, events_proj, events_per_day_atel)

        return "<tr>" + week + ' </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
       # events = chain(Article.objects.filter(start_time__year=self.year, start_time__month=self.month), Projet.objects.filter(start_time__year=self.year, start_time__month=self.month))

        events_arti = Article.objects.filter(start_time__year=self.year, start_time__month=self.month)
        events_proj = Projet.objects.filter(start_time__year=self.year, start_time__month=self.month)
        events_atel = Atelier.objects.filter(date_atelier__year=self.year, date_atelier__month=self.month)
        cal = '<table border="0" cellpadding="0" cellspacing="0" class="calendar table-condensed">\n'
        cal += self.formatmonthname(self.year, self.month, withyear=withyear)+'\n'
        cal += self.formatweekheader()+'\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += self.formatweek(week, events_arti, events_proj, events_atel)+'\n'
        cal += '</table>\n'
        return cal
