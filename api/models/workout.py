from django.db import models
from django.contrib.gis.db import models as geo_models
from .constants import WORKOUT_GENDER_PREFERENCES, EITHER
from .validators import PROFICIENCY_VALIDATORS, AGE_VALIDATORS, PEOPLE_MAX_VALIDATORS


class Workout(geo_models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )
    sport = models.ForeignKey(
        'Sport',
        on_delete=models.CASCADE,
    )
    desired_proficiency = models.IntegerField(
        validators=PROFICIENCY_VALIDATORS,
    )
    expected_gender = models.CharField(
        max_length=1,
        choices=WORKOUT_GENDER_PREFERENCES,
        default=EITHER,
    )
    # postgis adds an index by default to geo fields,
    # normally an index on the location field
    # would have to be added to Meta to prevent full scans of the table
    location = geo_models.PointField()
    location_name = models.CharField(max_length=100, default='')
    people_max = models.IntegerField(validators=PEOPLE_MAX_VALIDATORS)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    age_min = models.IntegerField(validators=AGE_VALIDATORS, default=None)
    age_max = models.IntegerField(validators=AGE_VALIDATORS, default=None)
    description = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.name
