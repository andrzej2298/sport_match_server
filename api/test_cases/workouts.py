from .base import TestBase, err
from .data import *

from api.models.constants import ACCEPTED


class WorkoutTest(TestBase):
    def test_workout_creation(self):
        self.create_user(JOHN)
        self.authenticate_user(JOHNS_CREDENTIALS)

        self.sport = JOHNS_RUNNING['sport']
        self.user_sport = self.add_user_sport(JOHNS_RUNNING)
        workout_a = dict(MIM_WORKOUT)
        workout_b = dict(BITWY_WARSZAWSKIEJ_WORKOUT)
        workout_a['sport'] = self.sport
        workout_b['sport'] = self.sport
        self.workout_a = self.add_workout(workout_a)
        self.workout_b = self.add_workout(workout_b)

    def test_suggestions_and_post_request(self):
        self.create_user(BOB)
        self.create_user(JOHN)

        # create workout
        self.authenticate_user(BOBS_CREDENTIALS)
        workout_id = self.add_workout(MIM_WORKOUT)

        # request to join workout
        self.authenticate_user(JOHNS_CREDENTIALS)
        suggestions = self.get_suggestions()
        suggestion = suggestions.data['results'][0]
        suggested_workout_id = suggestion['id']
        self.assertEqual(suggested_workout_id, workout_id)
        return suggested_workout_id

    def test_post_request(self):
        suggested_workout_id = self.test_suggestions_and_post_request()
        return self.post_request(suggested_workout_id).data['id']

    def test_react_to_request(self):
        request_id = self.test_post_request()

        # accept request
        self.authenticate_user(BOBS_CREDENTIALS)
        self.assertEqual(self.accept_request(request_id).data['status'], ACCEPTED)

    def test_empty_suggestions(self):
        self.test_react_to_request()
        suggestions = self.get_suggestions()
        self.assertTrue(not suggestions.data['results'])

    def test_sport_suggestions(self):
        self.create_user(BOB)
        self.create_user(JOHN)

        # create workout
        self.authenticate_user(BOBS_CREDENTIALS)
        workout_a = dict(MIM_WORKOUT)
        workout_b = dict(MIM_WORKOUT)
        sport_a = 1
        sport_b = 2
        workout_a['sport'] = sport_a
        workout_b['sport'] = sport_b
        id_a = self.add_workout(workout_a)
        self.add_workout(workout_b)

        # only one should be in suggestions
        self.authenticate_user(JOHNS_CREDENTIALS)
        suggestions = self.get_sport_suggestions(sport_a)
        self.assertEqual(suggestions.data['count'], 1)
        suggestion = suggestions.data['results'][0]
        suggested_workout_id = suggestion['id']
        self.assertEqual(suggested_workout_id, id_a)
