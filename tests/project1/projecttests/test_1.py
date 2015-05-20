# coding: utf-8
import logging

from django.test import SimpleTestCase
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from dj_timetravel_postgres.db_backend.base import DatabaseWrapper
from simpleapp.models import Simple


LOG = logging.getLogger('djtt.test')


class TestWorks(SimpleTestCase):
    def setUp(self):
        self.db_settings = settings.DATABASES.get('default').copy()

    def test_utf8(self):
        Simple.objects.create(name='árvíztűrő tükörfúrógép')
        o = Simple.objects.all()[0]
        self.assertEqual(u'árvíztűrő tükörfúrógép', o.name)
        Simple.objects.all().delete()

    def test_trigger(self):
        o = Simple.objects.create(name='árvíztűrő tükörfúrógép')
        o.name = 'árvíztűrő ütvefúrógép'
        o.save()
        Simple.objects.all().delete()

    def test_no_tt_schema(self):
        del self.db_settings['TT_SCHEMA']
        self.assertRaises(ImproperlyConfigured,
                          DatabaseWrapper, self.db_settings)

    def test_tt_schema_starts_with_pg_(self):
        self.db_settings['TT_SCHEMA'] = 'pg_something'
        self.assertRaises(ImproperlyConfigured,
                          DatabaseWrapper, self.db_settings)

    def test_tt_schema_not_string(self):
        self.db_settings['TT_SCHEMA'] = 1
        self.assertRaises(ImproperlyConfigured,
                          DatabaseWrapper, self.db_settings)

    def test_tt_schema_empty(self):
        self.db_settings['TT_SCHEMA'] = ''
        self.assertRaises(ImproperlyConfigured,
                          DatabaseWrapper, self.db_settings)

    def test_tt_schema_contains_double_quote(self):
        self.db_settings['TT_SCHEMA'] = '""'
        self.assertRaises(ImproperlyConfigured,
                          DatabaseWrapper, self.db_settings)
