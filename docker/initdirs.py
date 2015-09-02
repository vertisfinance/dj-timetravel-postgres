import click

from runutils import ensure_dir, run


@run.command()
def initdirs():
    click.echo('Make sure /data has permissions 777')
    ensure_dir('/data',
               owner='root', group='root', permsission_str='777')

    click.echo('Checking dir /data/logs')
    ensure_dir('/data/logs',
               owner='root', group='root', permsission_str='777')

    click.echo('Checking dir /data/logs/postgres')
    ensure_dir('/data/logs/postgres',
               owner='postgres', group='postgres', permsission_str='700')

    click.echo('Checking dir /data/logs/django')
    ensure_dir('/data/logs/django',
               owner='django', group='django', permsission_str='700')

    click.echo('Checking dir /data/logs/nginx')
    ensure_dir('/data/logs/nginx',
               owner='nginx', group='nginx', permsission_str='700')

    click.echo('Checking dir /data/sock')
    ensure_dir('/data/sock',
               owner='root', group='root', permsission_str='777')

    click.echo('Checking dir /data/backup')
    ensure_dir('/data/backup',
               owner='postgres', group='postgres', permsission_str='700')

    click.echo('Checking dir /data/static')
    ensure_dir('/data/static',
               owner='django', group='django', permsission_str='777')
