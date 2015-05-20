import logging
import importlib
import copy

from django.db import models
from django.apps import apps
from django.utils.encoding import python_2_unicode_compatible
from django.db.models.fields.proxy import OrderWrt
from django.conf import settings


LOG = logging.getLogger('djtt.models')


registered_models = {}


class TimeTravel(object):
    def contribute_to_class(self, cls, name):
        self.module = cls.__module__
        models.signals.class_prepared.connect(self.finalize, sender=cls)

    def finalize(self, sender, **kwargs):
        tt_model = self.create_tt_model(sender)

        module = importlib.import_module(self.module)
        setattr(module, tt_model.__name__, tt_model)

    def create_tt_model(self, model):
        attrs = {'__module__': self.module}

        app_module = '%s.models' % model._meta.app_label
        if model.__module__ != self.module:
            # registered under different app
            attrs['__module__'] = self.module
        elif app_module != self.module:
            # Abuse an internal API because the app registry is loading.
            app = apps.app_configs[model._meta.app_label]
            attrs['__module__'] = app.name  # full dotted name

        fields = self.copy_fields(model)
        attrs.update(fields)
        attrs.update(self.get_extra_fields(model, fields))
        # type in python2 wants str as a first argument
        attrs.update(Meta=type(str('Meta'), (), self.get_meta_options(model)))
        name = 'TT%s' % model._meta.object_name
        registered_models[model._meta.db_table] = model
        return python_2_unicode_compatible(
            type(str(name), (models.Model,), attrs))

    def copy_fields(self, model):
        fields = {}
        for field in model._meta.fields:
            field = copy.copy(field)
            field.rel = copy.copy(field.rel)
            if isinstance(field, OrderWrt):
                # OrderWrt is a proxy field, switch to a plain IntegerField
                field.__class__ = models.IntegerField
            if isinstance(field, models.ForeignKey):
                old_field = field
                field_arguments = {}
                if (getattr(old_field, 'one_to_one', False) or
                        isinstance(old_field, models.OneToOneField)):
                    FieldType = models.ForeignKey
                else:
                    FieldType = type(old_field)
                field_arguments['db_constraint'] = False
                field = FieldType(
                    old_field.rel.to,
                    related_name='+',
                    null=True,
                    blank=True,
                    primary_key=False,
                    db_index=True,
                    serialize=True,
                    unique=False,
                    on_delete=models.DO_NOTHING,
                    **field_arguments
                )
                field.name = old_field.name
            else:
                self.transform_field(field)
            fields[field.name] = field
        return fields

    def transform_field(self, field):
        field.name = field.attname
        if isinstance(field, models.AutoField):
            field.__class__ = models.IntegerField

        elif isinstance(field, models.FileField):
            # Don't copy file, just path.
            field.__class__ = models.TextField

        # Historical instance shouldn't change create/update timestamps
        field.auto_now = False
        field.auto_now_add = False

        if field.primary_key or field.unique:
            # Unique fields can no longer be guaranteed unique,
            # but they should still be indexed for faster lookups.
            field.primary_key = False
            field._unique = False
            field.db_index = True
            field.unique_for_date = False if field.unique_for_date else None
            field.unique_for_month = False if field.unique_for_month else None
            field.unique_for_year = False if field.unique_for_year else None
            field.serialize = True

    def get_extra_fields(self, model, fields):
        user_model = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

        def _str(tt_instance):
            params = (self.as_real_object,
                      self.tt_valid_from,
                      self.tt_valid_until)
            return '%s between %s and %s' % params

        return {
            'tt_id': models.AutoField(primary_key=True),
            'tt_valid_from': models.DecimalField(
                max_digits=18, decimal_places=6,
                default=0, auto_created=True),
            'tt_valid_until': models.DecimalField(
                max_digits=18, decimal_places=6,
                default=0, auto_created=True),
            'tt_user_modified': models.ForeignKey(
                user_model, null=True, related_name='+',
                on_delete=models.DO_NOTHING),
            'tt_user_deleted': models.ForeignKey(
                user_model, null=True, related_name='+',
                on_delete=models.DO_NOTHING),
            'tt_real_obj': models.ForeignKey(
                model, null=True, related_name='+',
                db_column='tt_real_obj',
                on_delete=models.DO_NOTHING),
            'as_real_object': AsRealObjectDescriptor(model),
            '__str__': lambda self: _str(self)
        }

    def get_meta_options(self, model):
        return {
            'db_table': 'tt_%s' % model._meta.db_table
        }


def register(model, app=None):
    if model._meta.db_table not in registered_models:
        tt = TimeTravel()
        tt.module = app and ("%s.models" % app) or model.__module__
        tt.finalize(model)
        registered_models[model._meta.db_table] = model


class AsRealObjectDescriptor(object):
    def __init__(self, model):
        self.model = model

    def __get__(self, instance, owner):
        values = (getattr(instance, f.attname)
                  for f in self.model._meta.fields)
        return self.model(*values)
