import sys
import os


def run_tests():
    # docker run -d --name djt \
    # -p 55432:5432 vertisfinance/dj-timetravel-postgres

    orig_path = sys.path[:]

    base = os.path.dirname(os.path.abspath(__file__))
    testdir = os.path.join(base, 'tests')
    modules_not_to_delete = sys.modules.keys()
    num_failures = 0

    for entry in os.listdir(testdir):

        # restore modules
        for module in sys.modules.keys():
            if module not in modules_not_to_delete:
                # print '--- %s' % module
                del sys.modules[module]
            # else:
            #     print '+++ %s' % module

        full = os.path.join(testdir, entry)
        if os.path.isdir(full):

            # add this to pythonpath
            sys.path = [full] + orig_path
            os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % entry

            from django.test.runner import DiscoverRunner
            from django.core.management import call_command
            import django

            django.setup()

            # clear migration files, makemigrations, migrate
            call_command('makemigrations', interactive=False, verbosity=1)
            call_command('migrate', interactive=False, verbosity=1)

            class NoDBRunner(DiscoverRunner):
                def setup_databases(self, **kwargs):
                    pass

                def teardown_databases(self, old_config, **kwargs):
                    pass

            test_runner = NoDBRunner()

            num_failures += test_runner.run_tests(['projecttests'])

    sys.exit(bool(num_failures))


if __name__ == '__main__':
    run_tests()
