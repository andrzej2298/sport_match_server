from django.contrib import admin
from .models.user import User
from .models.sport import Sport
from .models.user_sport import UserSport
from .models.workout import Workout
from .models.participation_request import ParticipationRequest

admin.site.register(User)
admin.site.register(Sport)
admin.site.register(UserSport)
admin.site.register(Workout)
admin.site.register(ParticipationRequest)

