from django.contrib.admin.sites import site

from roulette_app.models import Spin, Round

# Register your models here.

site.register(Spin)
site.register(Round)
