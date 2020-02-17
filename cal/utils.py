# cal/utils.py

from datetime import datetime
from calendar import LocaleHTMLCalendar, LocaleTextCalendar, month_name
from blog.models import Article, Projet, Evenement
from ateliers.models import Atelier
from django.db.models import Q

class Constantes:
    width = 10
    dicoJour = {"Monday".center(width): "Lundi".center(width), "Tuesday".center(width): "Mardi".center(width),
                "Wednesday".center(width): "Mercredi".center(width), "Thursday".center(width): "Jeudi".center(width),
                "Friday".center(width): "Vendredi".center(width), "Saturday".center(width): "Samedi".center(width),
                "Sunday".center(width): "Dimanche".center(width)}
    dicoMois = {"January".center(width): "Janvier".center(width), "February".center(width): "Février".center(width),
                "March".center(width): "Mars".center(width), "April".center(width): "Avril".center(width),
                "May".center(width): "Mai".center(width), "June".center(width): "Juin".center(width),
                "July".center(width): "Juillet".center(width), "August".center(width): "Août".center(width),
                "September".center(width): "Septembre".center(width), "October".center(width): "Octobre".center(width),
                "November".center(width): "Novembre".center(width), "December".center(width): "Décembre".center(width),
                }
class Calendar(LocaleTextCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        self.now = datetime.now
        super(Calendar, self).__init__()


    def getJourFrançais(self, weekday):
        jour = self.formatweekday(weekday, width=10)
        try:
            return Constantes.dicoJour[jour]
        except:
            return jour

    # formats a day as a td
    # filter events by day
    def formatday(self, request, day, weekday, events_arti, events_proj, events_atel, events_autre):
        events_per_day_arti = events_arti.filter(Q(start_time__day=day) | Q(start_time__day__lt=day, end_time__day__gte=day))
        events_per_day_proj = events_proj.filter(Q(start_time__day=day) | Q(start_time__day__lt=day, end_time__day__gte=day))
        events_per_day_autre = events_autre.filter(Q(start_time__day=day) | Q(start_time__day__lt=day, end_time__day__gte=day))
        events_per_day_atel = events_atel.filter(Q(date_atelier__day=day))

        d = ''
        for event in events_per_day_arti:
            if event.estPublic or (not request.user.is_anonymous and request.user.is_permacat):
                titre = event.titre if len(event.titre)<40 else event.titre[:37] + "..."
                d += "<div class='event'><a href='"+event.get_absolute_url() +"'><i class='fa fa-comments iconleft'></i> "+titre+'</a> </div>'
        for event in events_per_day_proj:
            if event.estPublic or (not request.user.is_anonymous and request.user.is_permacat):
                titre = event.titre if len(event.titre)<40 else event.titre[:37] + "..."
                d += "<div class='event'>  <a href='"+event.get_absolute_url() +"'><i class='fa fa-paper-plane iconleft' ></i> "+titre+'</a> </div>'
        for event in events_per_day_atel:
            titre = event.titre if len(event.titre)<40 else event.titre[:37] + "..."
            d += "<div class='event'> <a href='"+event.get_absolute_url() +"'><i class='fa fa-wrench iconleft' ></i> "+titre+'</a> </div>'

        for event in events_per_day_autre:
            if event.estPublic or (not request.user.is_anonymous and request.user.is_permacat):
                titre = event.gettitre if len(event.gettitre)<40 else event.gettitre[:37] + "..."
                d += "<div class='event'> <a href='"+event.get_absolute_url() +"'><i class='fa fa-comments iconleft' ></i> "+titre+'</a> </div>'

        now = datetime.now()
        aujourdhui=0
        if now.year > self.year or (now.year == self.year and now.month > self.month) :
            style = "style='background-color:#d9d9d9'"
        elif now.year == self.year and now.month == self.month and now.day > day:
            style = "style='background-color:#e6e6e6'"
        elif now.year == self.year and now.month == self.month and now.day == day:
            style = "style='background-color:#aeeaae; '"
            aujourdhui=1
        else:
            style = "style='background-color:#e6ffe6;'"

        ajoutPlus = "<a href='ajouterEvenement/?date="+ str(day) + "/" +str(self.month) +"/"+str(self.year) +"'><i class='fa fa-plus'></i></a>"
        #d += ajoutPlus
        if day != 0:
            ajout=""
            if weekday == 0:
                ajout= "<div class='event'>  <a href='/forum/article/visioconference'> <i class='fa fa-comments' ></i> Visioconférence</a> </div>"

            if aujourdhui == 1:
                return "<td "+style+" class='day'><span class=' badge badge-success joursemaine'>"+self.getJourFrançais(weekday) + " " + str(day)+ "</span><span class='datecourante'>"+str(day)+'</span>'+ajout + str(d)+'</td>'
            else:
                return "<td "+style+" class='day'><span class=' badge badge-dark joursemaine'>"+self.getJourFrançais(weekday)  + " " + str(day)+ "</span><span class='date'>"+str(day)+'</span>'+ajout +str(d)+ '</td>'


        return "<td class='other-month' style='background-color:white'></td>"

    # formats a week as a tr
    def formatweek(self, request, theweek, events_arti, events_proj, events_per_day_atel, events_autre):
        week = ''

        for d, weekday in theweek:
            week += self.formatday(request, d, weekday, events_arti, events_proj, events_per_day_atel, events_autre)

        return "<tr class='days'>" + week + ' </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, request, withyear=True):
       # events = chain(Article.objects.filter(start_time__year=self.year, start_time__month=self.month), Projet.objects.filter(start_time__year=self.year, start_time__month=self.month))

        events_arti = Article.objects.filter(start_time__year=self.year, start_time__month=self.month)
        events_proj = Projet.objects.filter(start_time__year=self.year, start_time__month=self.month)
        events_atel = Atelier.objects.filter(date_atelier__year=self.year, date_atelier__month=self.month)
        events_autre = Evenement.objects.filter(start_time__year=self.year, start_time__month=self.month)

        cal = '<table  class=" table-condensed" id="calendar">\n'
        #cal += self.formatmonthname(self.year, self.month, withyear=withyear)+'\n'

        for i in self.iterweekdays():
            cal += "<th  scope='col' class='weekdays'>"+ self.getJourFrançais(i) + '</th>'


        for week in self.monthdays2calendar(self.year, self.month):
            cal += self.formatweek(request, week, events_arti, events_proj, events_atel, events_autre)+'\n'
        cal += '</table>\n'
        return cal
