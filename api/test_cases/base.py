"""
Abstract test case class that implements useful methods used in real test cases.
"""

from rest_framework.test import APITestCase
from rest_framework import status
from sys import stderr

from api.models.constants import ACCEPTED
from .data import *


def err(*args):
    print(*args, file=stderr)


class TestBase(APITestCase):
    def create_user(self, user):
        self.user = self.register_user(user)

    def authenticate_user(self, user_credentials):
        token = self.get_token(user_credentials)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def reset_authentication(self):
        self.client.credentials()

    def get_suggestions(self):
        return self.client.get('/api/suggested_workouts/', format='json')

    def get_sport_suggestions(self, sport_id):
        return self.client.get(
            '/api/suggested_workouts/',
            {'sport': sport_id},
            format='json',
        )

    def post_request(self, workout_id):
        return self.client.post(
            '/api/participation_requests/',
            {
                'workout': workout_id,
                'message': 'abc',
            },
            format='json',
        )

    def accept_request(self, request_id):
        return self.client.patch(
            f'/api/participation_requests/{request_id}/',
            {
                'status': ACCEPTED,
            },
            format='json',
        )

    def add_sport(self, sport, success=True) -> int:
        return self.add_row(sport, '/api/sports/', success)

    def register_user(self, user, success=True) -> int:
        return self.add_row(user, '/api/register/', success)

    def add_workout(self, workout, success=True) -> int:
        return self.add_row(workout, '/api/hosted_workouts/', success)

    def add_user_sport(self, user_sport, success=True) -> int:
        return self.add_row(user_sport, '/api/user_sports/', success)

    def get_token(self, user_credentials, success=True) -> str:
        response = self.client.post('/api/login/', user_credentials, format='json')
        self.check(response, status.HTTP_200_OK, success)
        if success:
            return response.data['token']

    def check(self, response, expected_code, success):
        if success:
            if response.status_code != expected_code and hasattr(response, 'data'):
                err(response.data)
            self.assertEqual(response.status_code, expected_code)
        else:
            if response.status_code == expected_code and hasattr(response, 'data'):
                err(response.data)
            self.assertNotEqual(response.status_code, expected_code)

    def add_row(self, item, url, success) -> int:
        response = self.client.post(url, item, format='json')
        self.check(response, status.HTTP_201_CREATED, success)

        if success:
            return response.data['id']

