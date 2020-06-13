# from jardinpartage.views import accepter_participation
#
# def accepterParticipation(function):
#     def wrap(request, *args, **kwargs):
#
#         if request.user.is_jardinpartage:
#             return function(request, *args, **kwargs)
#         else:
#             raise accepter_participation(request, *args, **kwargs )
#     return wrap