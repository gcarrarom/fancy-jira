import click
from .issue import issue

@click.group()
@click.pass_context
def create(ctx):
    '''
    create commands!
    '''
    pass


create.add_command(issue)
