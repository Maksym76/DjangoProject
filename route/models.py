from django.db import models
from django.utils.translation import gettext_lazy


# Create your models here.

class Places(models.Model):
    name = models.CharField(max_length=50)


class Route(models.Model):
    starting_point = models.IntegerField()
    stopping_point = models.JSONField()
    destination = models.IntegerField()
    country = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    description = models.TextField()

    class RouteType(models.TextChoices):
        car = 'Car', gettext_lazy('Car')
        by_foot = 'Foot', gettext_lazy('Foot')

    route_type = models.CharField(max_length=50, choices=RouteType.choices, default=RouteType.by_foot)
    duration = models.IntegerField()


class Event(models.Model):
    id_route = models.IntegerField()
    event_admin = models.IntegerField()
    approve_user = models.JSONField()
    pending_users = models.JSONField()
    start_date = models.DateField()
    price = models.IntegerField()


class Review(models.Model):
    route_id = models.IntegerField()
    review_text = models.TextField()
    review_rate = models.IntegerField()
