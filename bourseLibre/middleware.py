# from django.utils.timezone import now
# from .models import Profil
#
# class SetLastVisitMiddleware(object):
#     def process_response(self, request, response):
#         if request.user.is_authenticated():
#             # Update last visit time after request finished processing.
#             Profil.objects.filter(pk=request.user.pk).update(last_visit=now())
#         return response
from django.shortcuts import render
from django.core.exceptions import RequestDataTooBig

class CheckRequest(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            body = request.body
        except RequestDataTooBig:
            return render(request, "513.html")

        return self.get_response(request)