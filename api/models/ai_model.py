from django.contrib.postgres.fields import JSONField
from django.db import models

from .user import User


class AIModel(models.Model):
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )
    model = JSONField()


def retrieve_model(user_id: int):
    obj, _ = AIModel.objects.get_or_create(
        id=user_id, defaults={'user': User.objects.get(id=user_id), 'model': {}}
    )
    return obj.model


def update_or_create_model(user_id: int, data: dict):
    AIModel.objects.filter(user__id=user_id).update(model=data)

