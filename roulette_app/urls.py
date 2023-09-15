from django.urls import path

from roulette_app.views import SpinView

urlpatterns = [
    path(
        "spin",
        SpinView.as_view({'post': 'create'}),
        name="spin",
    )]