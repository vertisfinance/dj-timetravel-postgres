import sys
import os
import subprocess
import time


def remove_container():
    with open('/dev/null', 'w') as devnull:
        try:
            subprocess.check_call(['docker', 'stop', 'djt'],
                                  stdout=devnull, stderr=devnull)
        except subprocess.CalledProcessError:
            pass

        try:
            subprocess.check_call(['docker', 'rm', 'djt'],
                                  stdout=devnull, stderr=devnull)
        except subprocess.CalledProcessError:
            pass


def run_container():
    with open('/dev/null', 'w') as devnull:
        subprocess.check_call(['docker', 'run', '-d', '--name', 'djt', '-p',
                               '55432:5432',
                               'vertisfinance/dj-timetravel-postgres'],
                              stdout=devnull, stderr=devnull)
    time.sleep(1)


def remove_migrations(path):
    for app in os.listdir(path):
        full = os.path.join(path, app)
        if os.path.isdir(full):
            mig = os.path.join(full, 'migrations')
            if os.path.isdir(mig):
                for migname in os.listdir(mig):
                    if migname != '__init__.py':
                        migfile = os.path.join(mig, migname)
                        os.remove(migfile)


def run_tests():
    orig_path = sys.path[:]

    base = os.path.dirname(os.path.abspath(__file__))
    testdir = os.path.join(base, 'tests')
    modules_not_to_delete = sys.modules.keys()
    num_failures = 0

    for entry in os.listdir(testdir):

        # restore modules
        for module in sys.modules.keys():
            if module not in modules_not_to_delete:
                del sys.modules[module]

        full = os.path.join(testdir, entry)
        if os.path.isdir(full):

            sys.path = [full] + orig_path
            os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % entry

            from django.test.runner import DiscoverRunner
            from django.core.management import call_command
            import django

            django.setup()

            remove_container()
            remove_migrations(full)
            run_container()

            call_command('makemigrations', interactive=False, verbosity=0)
            call_command('migrate', interactive=False, verbosity=0)

            class NoDBRunner(DiscoverRunner):
                def setup_databases(self, **kwargs):
                    pass

                def teardown_databases(self, old_config, **kwargs):
                    pass

            test_runner = NoDBRunner()
            num_failures += test_runner.run_tests(['projecttests'])

            remove_migrations(full)
            remove_container()

    sys.exit(bool(num_failures))


if __name__ == '__main__':
    run_tests()
