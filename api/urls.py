from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views
from .views.user_view_set import UserViewSet, CreateUserViewSet
from .views.workout_view_set import WorkoutViewSet, PendingWorkoutViewSet, HostedWorkoutViewSet, \
    RecentlyAcceptedWorkoutViewSet, RecentlyRejectedWorkoutViewSet
from .views.suggestions_view_set import SuggestedWorkoutViewSet
from .views.sport_view_set import SportViewSet
from .views.user_sport_view_set import UserSportViewSet
from .views.participation_request_view_set import ParticipationRequestViewSet

mock_router = routers.DefaultRouter()
router = routers.DefaultRouter()

router.register(r'register', CreateUserViewSet)
router.register(r'users', UserViewSet, basename='users')
router.register(r'workouts', WorkoutViewSet, basename='workouts')
router.register(r'hosted_workouts', HostedWorkoutViewSet, basename='hosted_workouts')
router.register(r'pending_workouts', PendingWorkoutViewSet, basename='pending_workouts')
router.register(r'recently_accepted_workouts', RecentlyAcceptedWorkoutViewSet, basename='recently_accepted')
router.register(r'recently_rejected_workouts', RecentlyRejectedWorkoutViewSet, basename='recently_rejected')
router.register(r'suggested_workouts', SuggestedWorkoutViewSet, basename='suggested_workouts')
router.register(r'sports', SportViewSet)
router.register(r'user_sports', UserSportViewSet, basename='user_sports')
router.register(r'participation_requests', ParticipationRequestViewSet, basename='participation_requests')

urlpatterns = [
    path('', include(router.urls)),
    path('mock/', include(mock_router.urls)),
    path('login/', views.obtain_auth_token),
]
