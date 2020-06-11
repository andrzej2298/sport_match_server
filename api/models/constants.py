# User constants
MALE = 'M'
FEMALE = 'F'
EITHER = 'E'

GENDERS = [
    (MALE, 'male'),
    (FEMALE, 'female'),
]

WORKOUT_GENDER_PREFERENCES = GENDERS + [(EITHER, 'either')]


# ParticipationRequest constants
PENDING = 'P'
ACCEPTED = 'A'
REJECTED = 'R'

STATUSES = [
    (PENDING, 'pending'),
    (ACCEPTED, 'accepted'),
    (REJECTED, 'rejected'),
]

SPORTS = [
    'running',
    'swimming',
    'cycling',
    'volleyball',
    'basketball',
    'soccer',
    'workout',
    'crossfit',
    'archery',
    'badminton',
    'other',
]

MIN_PROFICIENCY_VALUE = 0
MAX_PROFICIENCY_VALUE = 2
assert MIN_PROFICIENCY_VALUE < MAX_PROFICIENCY_VALUE
