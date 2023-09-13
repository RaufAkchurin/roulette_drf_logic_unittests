from django.core.validators import MaxValueValidator
from django.db import models


# Create your models here.

class SpinRound(models.Model):
    user = models.CharField(max_length=10)
    last_step = models.IntegerField(
        validators=[MaxValueValidator(limit_value=11)]
    )
