import click
from .remove import remove_config
from .set import set_config
from .show import show_config


@click.group()
@click.pass_context
def config(ctx):
    '''
    Group of commands to manage the jiractl command line
    '''
    pass


config.add_command(show_config)
config.add_command(set_config)
config.add_command(remove_config)


