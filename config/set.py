import click
from shared_functions import get_config, write_config_file

@click.command(name='set')
@click.option('--key', '-k', help="The key to be set in this command", required=True, prompt=True)
@click.option('--value', '-v', help="The value for the key to be used", required=True, prompt=True)
@click.pass_context
def set_config(ctx, key, value):
    '''
    Sets the key:value for a configuration to be used in all the commands

    Args:
        key (str): The key to be set
        value (str): The value for the key
    '''
    configuration = get_config()
    configuration[key] = value
    write_config_file(configuration['config_file_path'], configuration)