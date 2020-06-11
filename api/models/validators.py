from django.core.validators import MinValueValidator, MaxValueValidator

from api.models.constants import MIN_PROFICIENCY_VALUE, MAX_PROFICIENCY_VALUE

PROFICIENCY_VALIDATORS = [MinValueValidator(MIN_PROFICIENCY_VALUE), MaxValueValidator(MAX_PROFICIENCY_VALUE)]
AGE_VALIDATORS = [MinValueValidator(0), MaxValueValidator(120)]
PEOPLE_MAX_VALIDATORS = [MinValueValidator(2)]
