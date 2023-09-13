from django.shortcuts import render
from rest_framework import viewsets

from roulette_app.models import SpinRound
from roulette_app.serializers import SpinListSerializer


# Create your views here.

class RoundsViewSet(viewsets.ModelViewSet):
    queryset = SpinRound.objects.all()
    serializer_class = SpinListSerializer



