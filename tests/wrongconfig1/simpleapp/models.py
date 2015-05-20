from django.db import models


class Simple(models.Model):
    name = models.CharField('The name', max_length=50)
