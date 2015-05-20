import logging

from django.db.backends.postgresql_psycopg2 import base
from django.core.exceptions import ImproperlyConfigured

from .schema import DatabaseSchemaEditor


LOG = logging.getLogger('djtt.base')


class DatabaseWrapper(base.DatabaseWrapper):
    SchemaEditorClass = DatabaseSchemaEditor
    TT_SCHEMA_KEY = 'TT_SCHEMA'

    def is_valid_schema_name(self):
        if not isinstance(self.tt_schema, basestring):
            return False
        if self.tt_schema.startswith('pg_'):
            return False
        if self.tt_schema == '':
            return False
        if self.tt_schema.find('"') > -1:
            return False
        return True

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

        # Need to make sure this conn is only used by one thread
        self.allow_thread_sharing = False

        if self.TT_SCHEMA_KEY not in self.settings_dict:
            msg = ("dj_timetravel_postgres.db_backend requires %s to be "
                   "defined in the database settings "
                   "dict." % self.TT_SCHEMA_KEY)
            raise ImproperlyConfigured(msg)

        self.tt_schema = self.settings_dict.get(self.TT_SCHEMA_KEY, None)

        if not self.is_valid_schema_name():
            msg = "%s is not a valid schema name." % self.tt_schema
            raise ImproperlyConfigured(msg)
        else:
            self.quoted_tt_schema = self.ops.quote_name(self.tt_schema)
            LOG.debug('Quoted tt_schame name: %s' % self.quoted_tt_schema)
