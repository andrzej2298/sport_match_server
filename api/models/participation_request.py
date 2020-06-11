from django.db import models
from django.db.models.constraints import UniqueConstraint
from .constants import STATUSES, PENDING


class ParticipationRequest(models.Model):
    message = models.CharField(max_length=100)

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    workout = models.ForeignKey('Workout', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUSES, default=PENDING)
    seen = models.BooleanField(default=False)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'workout'], name='unique_user_workout')
        ]

    def __str__(self):
        return self.message
