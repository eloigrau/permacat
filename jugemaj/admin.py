"""Register jugemaj models in django admin."""
from django.contrib.admin import site

from .models import Candidate, Election, Vote

for model in [Election, Candidate, Vote]:
    site.register(model)
