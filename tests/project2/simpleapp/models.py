from django.db import models


class Simple2(models.Model):
    name = models.CharField('The name', max_length=100)
