import click
from .issues import issues
from .issue import issue
from .users import users

@click.group()
@click.pass_context
def get(ctx):
    '''
    get commands!
    '''
    pass


get.add_command(users)
get.add_command(issues)
get.add_command(issue)