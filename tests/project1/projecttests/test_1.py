from django.test import TestCase
from simpleapp.models import Simple


class VerySimple(TestCase):
    def test_something(self):
        Simple.objects.create(name='test')
        self.assertEqual(1, 1)
