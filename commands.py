import subprocess
import time
import os
import sys
import logging

import click
import django
from django.test.runner import DiscoverRunner
from django.core.management import call_command
from django.core.exceptions import ImproperlyConfigured


LOG = logging.getLogger('djtt.commands')


class NoDBRunner(DiscoverRunner):
    """
    Test runner that does not touch the database
    """
    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass


@click.group()
def run():
    pass


@run.command()
@click.argument('container_name')
def remove_container(container_name):
    """
    Stops and removes a docker container with the given name
    """
    with open('/dev/null', 'w') as devnull:
        try:
            subprocess.check_call(['docker', 'stop', container_name],
                                  stdout=devnull, stderr=devnull)
        except subprocess.CalledProcessError:
            pass

        try:
            subprocess.check_call(['docker', 'rm', container_name],
                                  stdout=devnull, stderr=devnull)
        except subprocess.CalledProcessError:
            pass


@run.command()
@click.argument('container_name')
def run_container(container_name):
    """
    Starts the database container with the given name.
    The db will listen on host port 55432.
    """
    with open('/dev/null', 'w') as devnull:
        subprocess.check_call(['docker', 'run', '-d', '--name', container_name,
                               '-p', '55432:5432',
                               'vertisfinance/dj-timetravel-postgres'],
                              stdout=devnull, stderr=devnull)
    time.sleep(1)


@run.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False))
def remove_migrations(path):
    """
    Removes all migration files from apps under the project given by path
    """
    for app in os.listdir(path):
        full = os.path.join(path, app)
        if os.path.isdir(full):
            mig = os.path.join(full, 'migrations')
            if os.path.isdir(mig):
                for migname in os.listdir(mig):
                    if migname != '__init__.py':
                        migfile = os.path.join(mig, migname)
                        os.remove(migfile)


@run.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False))
@click.option('--no_makemigrations', is_flag=True)
@click.option('--no_migrate', is_flag=True)
@click.option('--assert_error', is_flag=True)
def run_tests(path, no_makemigrations, no_migrate, assert_error):
    orig_path = sys.path[:]
    sys.path = [path] + orig_path
    os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

    try:
        django.setup()

        if no_makemigrations:
            pass
        else:
            call_command('makemigrations', interactive=False, verbosity=0)

        if no_migrate:
            pass
        else:
            call_command('migrate', interactive=False, verbosity=0)

    except ImproperlyConfigured:
        if not assert_error:
            raise
        else:
            LOG.info('Error occured as expected...')

    test_runner = NoDBRunner()
    num_failures = test_runner.run_tests(['projecttests'])

    sys.path = orig_path

    sys.exit(bool(num_failures))

if __name__ == '__main__':
    run()
