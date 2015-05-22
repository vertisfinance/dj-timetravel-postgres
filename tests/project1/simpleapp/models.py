from django.db import models
from django.contrib.auth.models import User

from dj_timetravel_postgres.models import TimeTravel, register


class Simple(models.Model):
    name = models.CharField('The name', max_length=50)

    timetravel = TimeTravel()

    def __unicode__(self):
        return 'Simple (%s)' % self.name


register(User, 'simpleapp')


class Complex(models.Model):
    simple = models.ForeignKey(Simple, primary_key=True)
    title = models.CharField(max_length=5)

    timetravel = TimeTravel()
