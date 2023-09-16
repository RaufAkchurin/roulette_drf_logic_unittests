from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# Create your models here.

# class User(models.Model):
#     name = models.CharField(max_length=8)
#
#     def __str__(self):
#         return f"id - {self.pk}    name - {self.name}"


class SpinRound(models.Model):
    round = models.IntegerField(default=1)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user",
    )
    last_step = models.IntegerField(
        validators=[MaxValueValidator(limit_value=11, message="last_step не должен быть больше 11."),
                    MinValueValidator(limit_value=1, message="last_step не должен быть меньше 0.")],
        default=1
    )
    rest_values = models.CharField(default='1,2,3,4,5,6,7,8,9,10', max_length=35)
    finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.round} round / {self.pk} id"

    class Meta:
        # Уникальность комбинации round и last_step
        unique_together = ('round', 'last_step')




