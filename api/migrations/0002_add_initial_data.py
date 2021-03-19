# Generated by Django 3.0.1 on 2020-03-21 12:54

from django.db import migrations
from api.models.constants import SPORTS


def add_initial_data(apps, schema_editor):
    Sport = apps.get_model('api', 'Sport')

    for sport in SPORTS:
        Sport.objects.create(name=sport)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_initial_data),
    ]