import click
import signal

from runutils import runbash, sleep, run_daemon, run


@run.command()
@click.argument('user', default='developer')
def shell(user):
    runbash(user)


@run.command()
def start():
    """Starts the service."""
    run_daemon(['dummy'], signal_to_send=signal.SIGINT, waitfunc=sleep)


if __name__ == '__main__':
    run()
