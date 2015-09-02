import signal
import time

import click
import psycopg2

from runutils import run_daemon, runbash, getvar, run


def waitfordb(stop_object):
    host = 'postgres'
    user = 'myvertis'
    password = getvar('DB_PASSWORD')

    for waitsec in [1, 1, 1, 2, 2, 2, 5, 5, 10, 10, 10, 30, 30, 30]:
        if stop_object.stopped:
            break

        try:
            psycopg2.connect(host=host, user=user, password=password)
        except psycopg2.OperationalError:
            click.echo('Waiting for db: %s second(s)' % waitsec)
            for i in range(10 * waitsec):
                if stop_object.stopped:
                    break
                time.sleep(0.1)
        else:
            break


@run.command()
@click.argument('user', default='developer')
def shell(user):
    runbash(user)


@run.command()
def start_runserver():
    start = ['django-admin.py', 'runserver', '0.0.0.0:8000']
    run_daemon(start, signal_to_send=signal.SIGINT, waitfunc=waitfordb,
               user='django')


@run.command()
def start_uwsgi():
    """Starts the service."""
    start = ["uwsgi", "--ini", getvar('INI_FILE')]

    run_daemon(start, signal_to_send=signal.SIGQUIT, user='django',
               waitfunc=waitfordb)


if __name__ == '__main__':
    run()
