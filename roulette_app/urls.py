from django.urls import path

from roulette_app.views import SpinView, StatisticView

urlpatterns = [
    path("spin", SpinView.as_view({'post': 'create'}), name="spin", ),
    path("statistic", StatisticView.as_view({'get': 'list'}), name="statistic", ),

]
