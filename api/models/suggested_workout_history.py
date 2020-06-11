from django.db import models, IntegrityError
from django.db.models.constraints import UniqueConstraint

from api.models.user import User
from api.models.workout import Workout


class SuggestedWorkoutHistoryItem(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    workout = models.ForeignKey('Workout', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'workout'], name='unique_user_suggested_workout')
        ]


def add_suggested_workout_to_history(workout: Workout, user: User):
    try:
        SuggestedWorkoutHistoryItem.objects.create(user=user, workout=workout)
    except IntegrityError:
        # unique (user, workout) constraint not satisfied, can't
        # add the object a second time
        return

    # keep number of objects below or equal 200
    count = SuggestedWorkoutHistoryItem.objects.filter(user=user).count()
    if count > 200:
        delete_count = count - 200
        SuggestedWorkoutHistoryItem.objects.order_by('id')[:delete_count].delete()
