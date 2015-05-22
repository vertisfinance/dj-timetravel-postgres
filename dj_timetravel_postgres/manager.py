import logging

from django.db import models


LOG = logging.getLogger('djtt.manager')


class TTDescriptor(object):
    def __init__(self, model):
        self.model = model

    def __get__(self, instance, owner):
        if instance is None:
            return TTManager(self.model)
        return TTManager(self.model, instance)


class TTManager(models.Manager):
    def __init__(self, model, instance=None):
        super(TTManager, self).__init__()
        self.model = model
        self.instance = instance

    def get_queryset(self):
        qs = super(TTManager, self).get_queryset()
        if self.instance is None:
            return qs

        key_name = self.instance._meta.pk.name
        return qs.filter(**{key_name: self.instance.pk})
