from django.db import models
from django.db.models.constraints import UniqueConstraint
from .validators import PROFICIENCY_VALIDATORS


class UserSport(models.Model):
    user = models.ForeignKey(
        'User', related_name='sport_list',
        on_delete=models.CASCADE,
    )
    sport = models.ForeignKey(
        'Sport',
        on_delete=models.CASCADE,
    )
    level = models.IntegerField(
        validators=PROFICIENCY_VALIDATORS,
    )

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'sport'], name='unique_user_sport')
        ]

    def __str__(self):
        return f'{self.user}\'s {self.sport}'
