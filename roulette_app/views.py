from django.shortcuts import render
from rest_framework import viewsets

from roulette_project.roulette_app.models import SpinRound
from roulette_project.roulette_app.serializers import SpinSerializer


# Create your views here.

class SpinViewSet(viewsets.ModelViewSet):
    queryset = SpinRound.objects.all()
    serializer_class = SpinSerializer
