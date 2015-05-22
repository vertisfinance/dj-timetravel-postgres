# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.db.models.deletion
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Simple',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'The name')),
            ],
        ),
        migrations.CreateModel(
            name='TTComplex',
            fields=[
                ('tt_valid_until', models.DecimalField(default=0, auto_created=True, max_digits=18, decimal_places=6)),
                ('tt_valid_from', models.DecimalField(default=0, auto_created=True, max_digits=18, decimal_places=6)),
                ('title', models.CharField(max_length=5)),
                ('tt_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'tt_simpleapp_complex',
            },
        ),
        migrations.CreateModel(
            name='TTSimple',
            fields=[
                ('tt_valid_until', models.DecimalField(default=0, auto_created=True, max_digits=18, decimal_places=6)),
                ('tt_valid_from', models.DecimalField(default=0, auto_created=True, max_digits=18, decimal_places=6)),
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'The name')),
                ('tt_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'tt_simpleapp_simple',
            },
        ),
        migrations.CreateModel(
            name='TTUser',
            fields=[
                ('tt_valid_until', models.DecimalField(default=0, auto_created=True, max_digits=18, decimal_places=6)),
                ('tt_valid_from', models.DecimalField(default=0, auto_created=True, max_digits=18, decimal_places=6)),
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', verbose_name='username', db_index=True)),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('tt_id', models.AutoField(serialize=False, primary_key=True)),
                ('tt_real_obj', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_column=b'tt_real_obj', to=settings.AUTH_USER_MODEL, null=True)),
                ('tt_user_deleted', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, null=True)),
                ('tt_user_modified', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'db_table': 'tt_auth_user',
            },
        ),
        migrations.CreateModel(
            name='Complex',
            fields=[
                ('simple', models.ForeignKey(primary_key=True, serialize=False, to='simpleapp.Simple')),
                ('title', models.CharField(max_length=5)),
            ],
        ),
        migrations.AddField(
            model_name='ttsimple',
            name='tt_real_obj',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_column=b'tt_real_obj', to='simpleapp.Simple', null=True),
        ),
        migrations.AddField(
            model_name='ttsimple',
            name='tt_user_deleted',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='ttsimple',
            name='tt_user_modified',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='ttcomplex',
            name='simple',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='simpleapp.Simple', null=True),
        ),
        migrations.AddField(
            model_name='ttcomplex',
            name='tt_user_deleted',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='ttcomplex',
            name='tt_user_modified',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='ttcomplex',
            name='tt_real_obj',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_column=b'tt_real_obj', to='simpleapp.Complex', null=True),
        ),
    ]
