from datetime import datetime

YEAR = datetime.now().year + 1

MIM_COORDINATES = [
    52.211769,
    20.982064
]

MIM_LOCATION = {
    'type': 'Point',
    'coordinates': MIM_COORDINATES,
}

JOHNS_CREDENTIALS = {
    'username': 'John',
    'password': 'secret',
}

BOBS_CREDENTIALS = {
    'username': 'Bob',
    'password': 'secret',
}

ADDITIONAL_INFO = {
    'email': 'john@example.com',
    'birth_date': '2020-02-06',
    'gender': 'M',
    'description': 'abc',
    'phone_number': '999999999',
    'location': MIM_LOCATION,
}

JOHN = {
    **JOHNS_CREDENTIALS,
    **ADDITIONAL_INFO,
}

BOB = {
    **BOBS_CREDENTIALS,
    **ADDITIONAL_INFO,
}

JOHNS_RUNNING = {
    'level': 0,
    'sport': 1
}
MIM_WORKOUT = {
    'name': 'MIM',
    'people_max': 10,
    'desired_proficiency': 0,
    'location': MIM_LOCATION,
    'location_name': 'mim',
    'level': 9,
    'start_time': f'{YEAR}-10-10T01:01:00Z',
    'end_time': f'{YEAR}-10-10T01:01:00Z',
    'description': 'abc',
    'age_min': 0,
    'age_max': 90,
    'sport': 1,
    'expected_gender': 'E',
}

BITWY_WARSZAWSKIEJ_COORDINATES = [
    52.211858,
    20.977279
]

BITWY_WARSZAWSKIEJ_WORKOUT = {
    'name': 'Bitwy Warszawskiej',
    'people_max': 10,
    'desired_proficiency': 0,
    'location': {
        'type': 'Point',
        'coordinates': BITWY_WARSZAWSKIEJ_COORDINATES,
    },
    'location_name': 'bw',
    'level': 9,
    'start_time': f'{YEAR}-10-10T01:01:00Z',
    'end_time': f'{YEAR}-10-10T01:01:00Z',
    'description': 'abc',
    'age_min': 0,
    'age_max': 90,
    'sport': 1,
    'expected_gender': 'E',
}

