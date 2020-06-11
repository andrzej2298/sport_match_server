from django.contrib.postgres.fields import JSONField
from django.db import models


class AIModel(models.Model):
    model = JSONField()


def retrieve_model():
    return AIModel.objects.get(id=1).model


def update_or_create_model(data: dict):
    AIModel.objects.filter(id=1).update(model=data)

