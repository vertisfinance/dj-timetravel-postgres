# coding: utf-8
import logging

from django.test import SimpleTestCase, TestCase
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from dj_timetravel_postgres.db_backend.base import DatabaseWrapper
from simpleapp.models import Simple, Complex


LOG = logging.getLogger('djtt.test')


class TestNoDB(SimpleTestCase):
    def setUp(self):
        self.db_settings = settings.DATABASES.get('default').copy()

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

    def test_keepdb(self):
        o1 = Simple(name='first')
        o1.save()
        # o2 = Simple.objects.create(name='second')
        # o3 = Simple.objects.create(name='third')
        # o4 = Simple.objects.create(name='fourth')

        c1 = Complex(simple=o1, title='mr')
        c1.save()

        for tt in c1.tt_objects.all():
            LOG.info('tt record: %s' % tt)


# class TestDB(TestCase):
#     def test_insertion(self):
#         o1 = Simple.objects.create(name='first')
#         self.assertEqual(len(Simple.tt_objects.all()), 1)

#         o2 = Simple.objects.create(name='second')
#         self.assertEqual(len(Simple.tt_objects.all()), 2)

#         o1.name = 'new first'
#         o1.save()
#         self.assertEqual(len(Simple.tt_objects.all()), 3)

#         # it did not really changed, no need to save
#         o2.name = 'second'
#         o2.save()
#         self.assertEqual(len(Simple.tt_objects.all()), 3)

#         o2.name = 'new second'
#         o2.save()
#         self.assertEqual(len(Simple.tt_objects.all()), 4)

#         LOG.debug('o2 tt length: %s' % len(o2.tt_objects.all()))

#         for tt in o2.tt_objects.all():
#             LOG.debug(tt)
