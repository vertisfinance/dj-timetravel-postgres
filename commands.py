import subprocess
import time
import os
import sys
import logging

import click
import django
from django.test.runner import DiscoverRunner
from django.core.management import call_command


LOG = logging.getLogger('djtt.commands')
CONTAINER_NAME = 'djtt'
IMAGE_NAME = 'vertisfinance/dj-timetravel-postgres'
BROWSER = 'chromium-browser'


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


def remove_container():
    """
    Stops and removes a docker container with the given name
    """
    with open('/dev/null', 'w') as devnull:
        try:
            subprocess.check_call(['docker', 'stop', CONTAINER_NAME],
                                  stdout=devnull, stderr=devnull)
        except subprocess.CalledProcessError:
            pass

        try:
            subprocess.check_call(['docker', 'rm', CONTAINER_NAME],
                                  stdout=devnull, stderr=devnull)
        except subprocess.CalledProcessError:
            pass


def run_container():
    """
    Starts the database container with the given name.
    The db will listen on host port 55432.
    """
    with open('/dev/null', 'w') as devnull:
        subprocess.check_call(['docker', 'run', '-d', '--name', CONTAINER_NAME,
                               '-p', '55432:5432', IMAGE_NAME],
                              stdout=devnull, stderr=devnull)
    time.sleep(1)


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


def erase_coverage():
    subprocess.call(['coverage', 'combine'])
    subprocess.call(['coverage', 'erase'])


def coverage_report(browser=False):
    subprocess.call(['coverage', 'combine'])
    if browser:
        subprocess.call(['coverage', 'html'])
        subprocess.call([BROWSER, 'htmlcov/index.html'])
    else:
        subprocess.call(['coverage', 'report', '-m'])


@run.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False))
@click.option('--delete_migrations', is_flag=True)
@click.option('--make_migrations', is_flag=True)
@click.option('--do_migrate', is_flag=True)
@click.option('--reset_db', is_flag=True)
@click.option('--exception_class_name', default=None)
@click.option('--settings_module', default='core.settings')
def run_projecttests(path,
                     delete_migrations,
                     make_migrations,
                     do_migrate,
                     reset_db,
                     exception_class_name,
                     settings_module):
    """
    Because of django setup, this must be run in subprocess.
    """
    if reset_db:
        remove_container()
        run_container()

    orig_path = sys.path[:]
    sys.path = [path] + orig_path
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module

    raised_exception_class_name = None
    raised_exception_instance = None

    if delete_migrations:
        remove_migrations(path)

    try:
        django.setup()
        if make_migrations:
            call_command('makemigrations', interactive=False, verbosity=0)
        if do_migrate:
            call_command('migrate', interactive=False, verbosity=0)
    except Exception as e:
        raised_exception_class_name = e.__class__.__name__
        raised_exception_instance = e

    if exception_class_name:
        if raised_exception_class_name is None:
            msg = 'Exception "%s" not raised.' % exception_class_name
            raise Exception(msg)
        if raised_exception_class_name != exception_class_name:
            raise raised_exception_instance
    else:
        if raised_exception_instance:
            raise raised_exception_instance

    test_runner = NoDBRunner()
    num_failures = test_runner.run_tests(['projecttests'])
    sys.path = orig_path
    sys.exit(bool(num_failures))


def call_projecttests(path,
                      delete_migrations=True,
                      make_migrations=True,
                      do_migrate=True,
                      reset_db=True,
                      exception_class_name=None):
    params = [
        'coverage', 'run', '-p', '--branch', '--source',
        'dj_timetravel_postgres',
        'commands.py', 'run_projecttests', path
    ]
    if delete_migrations:
        params.append('--delete_migrations')
    if make_migrations:
        params.append('--make_migrations')
    if do_migrate:
        params.append('--do_migrate')
    if reset_db:
        params.append('--reset_db')
    if exception_class_name:
        params += ['--exception_class_name', exception_class_name]

    subprocess.check_call(params)


@run.command()
@click.option('--browser', '-b', is_flag=True)
def suite(browser):
    erase_coverage()

    # call_projecttests('tests/wrongconfig1',
    #                   exception_class_name='ImproperlyConfigured')
    # call_projecttests('tests/wrongconfig2',
    #                   exception_class_name='ImproperlyConfigured')
    call_projecttests('tests/project1')

    coverage_report(browser)


if __name__ == '__main__':
    run()
