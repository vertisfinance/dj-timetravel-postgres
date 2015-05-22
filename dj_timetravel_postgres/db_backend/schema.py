import logging

from django.db.backends.postgresql_psycopg2 import schema
from django.db.migrations.state import ModelState


LOG = logging.getLogger('djtt.schema')


class DatabaseSchemaEditor(schema.DatabaseSchemaEditor):

    sql_schemas = "SELECT schema_name FROM information_schema.schemata"

    sql_create_schema = "CREATE SCHEMA %s"

    sql_now = "EXTRACT(EPOCH FROM NOW())"

    # #### TODO: the user table pk can be something else than integer!!!
    sql_create_tttable = """
        CREATE TABLE %s.timetravel (
            pid INTEGER,
            user_id INTEGER,
            ts NUMERIC(18,6))"""

    sql_trigger_insert = "INSERT INTO %(table)s (%(cols)s) VALUES (%(vals)s)"

    sql_end_of_time = "999999999999"

    sql_trigger_update = """
        UPDATE %(table)s
        SET tt_valid_until = %(now)s,
            tt_user_%(action)s_id = ($1)
        WHERE %(pk_field)s = ($2).%(pk_field)s
        AND tt_valid_until = %(eot)s"""

    # #### TODO: the user table pk can be something else than integer!!!
    sql_triggerfunc = """
        CREATE OR REPLACE FUNCTION %(funcname)s()
        RETURNS TRIGGER AS $func$
        DECLARE usr INT;
        BEGIN
            SELECT user_id INTO usr
            FROM %(schema)s.timetravel
            WHERE pid = PG_BACKEND_PID();

            IF TG_OP = 'DELETE' THEN
                EXECUTE $$%(del_upd_stmt)s$$ USING usr, OLD;
                RETURN OLD;
            ELSIF TG_OP = 'UPDATE' THEN
                IF NEW != OLD THEN
                    EXECUTE $$%(upd_upd_stmt)s$$ USING usr, OLD;
                    EXECUTE $$%(insert_stmt)s$$ USING usr, NEW;
                END IF;
                RETURN NEW;
            ELSE
                EXECUTE $$%(insert_stmt)s$$ USING usr, NEW;
                RETURN NEW;
            END IF;
            RETURN NULL;
        END;
        $func$ LANGUAGE plpgsql"""

    sql_trigger = """
        DROP TRIGGER IF EXISTS %(triggername)s ON %(table)s;
        CREATE TRIGGER %(triggername)s
        AFTER INSERT OR UPDATE OR DELETE ON %(table)s
        FOR EACH ROW EXECUTE PROCEDURE %(funcname)s()
    """

    def __init__(self, *args, **kwargs):
        super(DatabaseSchemaEditor, self).__init__(*args, **kwargs)
        self.schema_ok = False

    def _real_model(self, model):
        return model.tt_real_obj.field.rel.to

    def _ensure_schema(self):
        """
        Creates timetravel schema and the table "timetravel"
        if the schema does not exist.
        """
        if not self.schema_ok:
            tt_schema = self.connection.tt_schema
            quoted_tt_schema = self.connection.quoted_tt_schema
            cursor = self.connection.cursor()
            cursor.execute(self.sql_schemas)
            existing = [row[0] for row in cursor.fetchall()]
            if tt_schema not in existing:
                cursor.execute(self.sql_create_schema % quoted_tt_schema)
                cursor.execute(self.sql_create_tttable % quoted_tt_schema)
                LOG.debug('schema %s created' % quoted_tt_schema)
            self.schema_ok = True

    def _get_trigger_insert_stmt(self, model):
        cols = ['tt_valid_from', 'tt_valid_until',
                'tt_user_modified_id', 'tt_user_deleted_id',
                'tt_real_obj']
        vals = [self.sql_now, self.sql_end_of_time, '$1', 'NULL', 'NULL']
        for field in model._meta.local_fields:
            definition, _ = self.column_sql(model, field)
            col = field.column
            if definition is None or col in cols or col == 'tt_id':
                continue
            cols.append(field.column)
            vals.append('($2).%s' % self.quote_name(field.column))
        cols = ','.join([self.quote_name(c) for c in cols])
        vals = ','.join(vals)

        return self.sql_trigger_insert % {
            'table': model._meta.db_table,
            'cols': cols,
            'vals': vals
        }

    def _recreate_triggerfunc(self, model):
        insert_stmt = self._get_trigger_insert_stmt(model)
        params = {
            'table': model._meta.db_table,
            'action': 'modified',
            'pk_field': self._real_model(model)._meta.pk.column,
            'eot': self.sql_end_of_time,
            'now': self.sql_now
        }
        upd_upd_stmt = self.sql_trigger_update % params
        params['action'] = 'deleted'
        del_upd_stmt = self.sql_trigger_update % params
        sql = self.sql_triggerfunc % {
            'funcname': '%s_tf' % model._meta.db_table,
            'schema': self.connection.quoted_tt_schema,
            'del_upd_stmt': del_upd_stmt,
            'upd_upd_stmt': upd_upd_stmt,
            'insert_stmt': insert_stmt
        }
        cursor = self.connection.cursor()
        cursor.execute(sql)

    def _recreate_trigger(self, model):
        sql = self.sql_trigger % {
            'triggername': '%s_tg' % model._meta.db_table,
            'table': self._real_model(model)._meta.db_table,
            'funcname': '%s_tf' % model._meta.db_table
        }
        cursor = self.connection.cursor()
        cursor.execute(sql)

    def recreate_objects(self, model):
        if hasattr(model, 'tt_real_obj'):
            LOG.debug('Recreating objects for %s' % model._meta.model_name)
            self._ensure_schema()
            self._recreate_triggerfunc(model)
            self._recreate_trigger(model)

    def delete_objects(self, model):
        pass

    def rename_objects(self, model, old_db_table, new_db_table):
        pass

    # Actions

    def create_model(self, model):
        super(DatabaseSchemaEditor, self).create_model(model)
        self.recreate_objects(model)

    def delete_model(self, model):
        super(DatabaseSchemaEditor, self).delete_model(model)
        self.delete_objects(model)

    def alter_db_table(self, model, old_db_table, new_db_table):
        super(DatabaseSchemaEditor, self).alter_db_table(
            model, old_db_table, new_db_table)
        self.rename_objects(model, old_db_table, new_db_table)

    # The following methods are different:
    # recreate_objects needs to know the NEW model, but we do not
    # have access to the new state. State altering must be 'emulated'.

    def add_field(self, model, field):
        super(DatabaseSchemaEditor, self).add_field(model, field)

        # ModelState.render needs to have an apps to render into.
        _apps = model._meta.apps.clone()

        # get a state
        _model_state = ModelState.from_model(model)

        # add the field
        _model_state.fields.append((field.name, field))

        # get a model back
        model = _model_state.render(_apps)

        self.recreate_objects(model)

    def remove_field(self, model, field):
        super(DatabaseSchemaEditor, self).remove_field(model, field)
        # self.recreate_objects(model)

    def alter_field(self, model, old_field, new_field, strict=False):
        super(DatabaseSchemaEditor, self).alter_field(
            model, old_field, new_field, strict)
        # self.recreate_objects(model)

    # For reference

    # If we decide to handle indexes in an advanced way, we may need these
    # methods:

    # def alter_unique_together(self, model, old_unique_together,
    #                           new_unique_together):
    #     super(DatabaseSchemaEditor, self).alter_unique_together(
    #         model, old_unique_together, new_unique_together)

    # def alter_index_together(self, model, old_index_together,
    #                          new_index_together):
    #     super(DatabaseSchemaEditor, self).alter_index_together(
    #         model, old_index_together, new_index_together)

    # We probably won't need the following:

    # def alter_db_tablespace(self, model, old_db_tablespace,
    #                         new_db_tablespace):
    #     super(DatabaseSchemaEditor, self).alter_db_tablespace(
    #         model, old_db_tablespace, new_db_tablespace)
