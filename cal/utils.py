# cal/utils.py

from datetime import datetime
from calendar import LocaleHTMLCalendar, LocaleTextCalendar, month_name
from blog.models import Article, Projet
from ateliers.models import Atelier
from django.db.models import Q

class Constantes:
    dicoJour = {"monday":"lundi", "tuesday":"mardi", "wednesday":"mercredi", "thursday":"jeudi", "friday":"vendredi", "saturday":"samedi", "sunday":"dimanche"}
class Calendar(LocaleTextCalendar):
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
            titre = event.titre if len(event.titre)<50 else event.titre[:47] + "..."
            d += "<div class=' event'> <a href='"+event.get_absolute_url() +"'>"+titre+'</a> </div>'
        for event in events_per_day_proj:
            titre = event.titre if len(event.titre)<50 else event.titre[:47] + "..."
            d += "<div class=' event'> <a href='"+event.get_absolute_url() +"'>"+titre+'</a> </div>'

        now = datetime.now()
        aujourdhui=0
        if now.year > self.year or (now.year == self.year and now.month > self.month) :
            style = "style='background-color:grey'"
        elif now.year == self.year and now.month == self.month and now.day > day:
            style = "style='background-color:#bbeebb'"
        elif now.year == self.year and now.month == self.month and now.day == day:
            style = "style='background-color:#85e085; '"
            aujourdhui=1
        else:
            style = "style='background-color:#ccffcc;'"

        if day != 0:
            if aujourdhui == 1:
                return "<td "+style+" class='day'><span class='datecourante'>"+str(day)+'</span>'+str(d)+'</td>'
            else:
                return "<td "+style+" class='day'><span class='date'>"+str(day)+'</span>'+str(d)+'</td>'

        return "<td class='other-month' style='background-color:lightgrey'></td>"

    # formats a week as a tr
    def formatweek(self, theweek, events_arti, events_proj, events_per_day_atel):
        week = ''

        for d, weekday in theweek:
            week += self.formatday(d, events_arti, events_proj, events_per_day_atel)

        return "<tr class='days'>" + week + ' </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
       # events = chain(Article.objects.filter(start_time__year=self.year, start_time__month=self.month), Projet.objects.filter(start_time__year=self.year, start_time__month=self.month))

        events_arti = Article.objects.filter(start_time__year=self.year, start_time__month=self.month)
        events_proj = Projet.objects.filter(start_time__year=self.year, start_time__month=self.month)
        events_atel = Atelier.objects.filter(date_atelier__year=self.year, date_atelier__month=self.month)


        cal = '<div class="row moiscal"><div class="col-sm-12 ">' + self.formatmonthname(self.year, self.month, withyear=withyear, width=15)+ '</div></div>\n'
        cal += '<table  class=" table-condensed" id="calendar">\n'
        #cal += self.formatmonthname(self.year, self.month, withyear=withyear)+'\n'

        for i in self.iterweekdays():
            try:
                cal += "<th class='weekdays'>"+ Constantes.dicoJour[self.formatweekday(i, width=10)]+ '</th>'
            except:
                cal += "<th class='weekdays'>"+ self.formatweekday(i, width=10)+ '</th>'


        for week in self.monthdays2calendar(self.year, self.month):
            cal += self.formatweek(week, events_arti, events_proj, events_atel)+'\n'
        cal += '</table>\n'
        print (cal)
        return cal
