SECRET_KEY = 'test'

INSTALLED_APPS = (
    # 'django.contrib.auth',
    # 'django.contrib.contenttypes',

    # 'simpleapp',
)

DATABASES = {
    'default': {
        'ENGINE': 'dj_timetravel_postgres.db_backend',
        'HOST': 'localhost',
        'PORT': '55432',
        'NAME': 'timetravel',
        'USER': 'postgres',
        # 'TT_SCHEMA':  'history'
    }
}

LOGGING_CONFIG = None

import logging

fmt = ('%(levelname)s | %(name)s | %(lineno)d | %(message)s')
formatter = logging.Formatter(fmt)

h = logging.StreamHandler()
h.setFormatter(formatter)

l = logging.getLogger('djtt')
l.addHandler(h)
l.setLevel(logging.DEBUG)
