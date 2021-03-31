import click
from .issue import issue

@click.group()
@click.pass_context
def update(ctx):
    '''
    update commands!
    '''
    pass

update.add_command(issue)
