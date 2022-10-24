from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from django.db import models
from datetime import datetime
import json


# Create your models here.

def validate_stopping_point(value):
    try:
        stopping = json.loads(value)
        for itm in stopping:
            if 'name' in itm and 'lat' in itm and 'lon' in itm:
                continue
            else:
                raise ValidationError('ERROR')

    except BaseException:
        raise ValidationError('Not exists nursery field')


def validate_route_type(value):
    if value.title() not in ["Car", "Foot"]:
        raise ValidationError('ERROR')


def validate_date(value):
    try:
        parsed_date = datetime.strptime(value, "%Y-%m-%d")

    except BaseException:
        raise ValidationError('ERROR')

    if datetime.today() > parsed_date:
        raise ValidationError('ERROR')


class Places(models.Model):
    name = models.CharField(max_length=50)


class Route(models.Model):
    starting_point = models.IntegerField()
    stopping_point = models.CharField(max_length=50)
    destination = models.IntegerField()
    country = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    description = models.TextField()

    class RouteType(models.TextChoices):
        car = 'Car', gettext_lazy('Car')
        by_foot = 'Foot', gettext_lazy('Foot')

    route_type = models.CharField(max_length=50, choices=RouteType.choices, default=RouteType.by_foot,
                                  validators=[validate_route_type])
    duration = models.IntegerField()


class Event(models.Model):
    id_route = models.IntegerField()
    event_admin = models.IntegerField()
    event_user = models.CharField(max_length=50, null=True)
    start_date = models.DateField(validators=[validate_date])
    price = models.IntegerField()


class Review(models.Model):
    route_id = models.IntegerField()
    review_text = models.TextField()
    review_rate = models.IntegerField()
