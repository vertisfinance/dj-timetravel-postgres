from django.db import models
from django.contrib.auth.models import User

from dj_timetravel_postgres.models import TimeTravel, register


class Simple(models.Model):
    name = models.CharField('The name', max_length=50)
    timetravel = TimeTravel()


register(User, 'simpleapp')
