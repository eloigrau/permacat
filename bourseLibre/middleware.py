# from django.utils.timezone import now
# from .models import Profil
#
# class SetLastVisitMiddleware(object):
#     def process_response(self, request, response):
#         if request.user.is_authenticated():
#             # Update last visit time after request finished processing.
#             Profil.objects.filter(pk=request.user.pk).update(last_visit=now())
#         return response