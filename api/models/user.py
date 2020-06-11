from django.db import models
from django.contrib.gis.db import models as geo_models
from django.contrib.auth.models import User as DjangoUser
from django.core.validators import RegexValidator
from .constants import GENDERS


class User(models.Model):
    auth_user = models.OneToOneField(
        DjangoUser,
        on_delete=models.CASCADE
    )

    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDERS)
    description = models.CharField(max_length=200, default='')
    phone_number = models.CharField(validators=[RegexValidator(regex=r'^\d{9}$')], max_length=9, default="")
    location = geo_models.PointField()

    def __str__(self):
        return self.auth_user.username

    def natural_key(self):
        return self.auth_user.username
