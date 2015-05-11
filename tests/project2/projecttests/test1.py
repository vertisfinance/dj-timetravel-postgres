from django.test import TestCase
from simpleapp.models import Simple2


class VerySimple(TestCase):
    def test_something(self):
        Simple2.objects.create(name='test')
        self.assertEqual(1, 1)
