from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Round(models.Model):
    numbers = models.JSONField(default=dict)
    finished = models.BooleanField(default=False)

    @classmethod
    def logging(cls, _round, num, user):
        _round.numbers.update({num: user.id})
        _round.save()
        _round.refresh_from_db()

    def __str__(self):
        return f"id - {self.id}, numbers - {self.numbers}"


class Spin(models.Model):
    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        related_name="round_log",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_spins",
    )
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.round} round / {self.user_id} user_id / {self.pk} id"



