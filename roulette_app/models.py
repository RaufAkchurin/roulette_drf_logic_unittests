from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# Create your models here.

class SpinRound(models.Model):
    round = models.IntegerField(default=0)
    user = models.CharField(max_length=10)
    last_step = models.IntegerField(
        validators=[MaxValueValidator(limit_value=11),
                    MinValueValidator(limit_value=0, message="last_step не должен быть меньше 0.")]
    )

    def __str__(self):
        return f"{self.pk}"

    class Meta:
        # Уникальность комбинации round и last_step
        unique_together = ('round', 'last_step')
