import click
import rich
from shared_functions import get_config

@click.command(name="show")
@click.argument('key', required=False)
@click.pass_context
def show_config(ctx, key):
    '''
    Shows the current configuration file for JIRA communication and default values

    Args:
        key (str): the key to show
    '''
    configuration = get_config()
    configuration['apikey'] = "**********"
    del configuration['headers']
    if not key:
        rich.print(configuration)
    elif configuration.get(key):
        print(configuration[key])