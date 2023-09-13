from django.contrib import admin
from django.contrib.admin.sites import site

from roulette_app.models import SpinRound

# Register your models here.

site.register(SpinRound)
