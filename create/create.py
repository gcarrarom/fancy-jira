import click
from .issue import issue
from .comment import comment

@click.group()
@click.pass_context
def create(ctx):
    '''
    create commands!
    '''
    pass


create.add_command(issue)
create.add_command(comment)