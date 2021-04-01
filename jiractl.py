import os
import click
import json
import requests
import rich
from rich.markdown import Markdown
from rich.traceback import install
install()

import get
import update
import create

APP_NAME = '.jiractl'
CONFIG_FILE = 'config.json'

@click.group()
@click.pass_context
def jira(ctx):
    '''
    JIRA Command Line Interface
    '''
    app_dir = click.get_app_dir(APP_NAME)
    config_file_path = os.path.join(app_dir, CONFIG_FILE)
    config = read_configfile(config_file_path)
    if ctx.invoked_subcommand != 'login':
        try:
            config['authenticated'] = True
            config['headers'] = {"Authorization": f"Bearer {config['apikey']}",
                                "Content-Type": "application/json", 
                                "Accept": "application/json"}
        except KeyError:
            rich.print("You should authenticate with 'jira login' first!")
        config['api_endpoint'] = config['endpoint'] + "/rest/api"
    config['app_dir'] = app_dir
    config['config_file_path'] = config_file_path
    [os.environ.setdefault(key, config[key]) for key in config if key not in ['app_dir', 'endpoint', 'config_file_path', 'authenticated', 'headers']]
    ctx.obj = config

@click.command()
@click.option('--apikey', '-k', help="API Key for the user authentication", required=True, prompt=True, hide_input=True)
@click.option('--endpoint', '-e', help="the URI of the Jira website for your company", required=True, prompt=True)
@click.pass_context
def login(ctx, apikey, endpoint):
    '''
    Setup of the authentication values for the JIRA Rest API

    Args:
        username (string): User ID to be used for the authentication
        password (string): Password of the user to be used for the authentication
        endpoint (string): URL of the Jira website managed by your company
    '''
    headers = {"Authorization": f"Bearer " + apikey,
                                "Content-Type": "application/json"}
    request = requests.get(endpoint + '/rest/api/latest/myself', headers=headers)
    request.raise_for_status()
    current_user = request.json()
    write_config_file(ctx.obj['config_file_path'], {'apikey': apikey,'endpoint': endpoint, 'current_user': current_user['key']})
    print("Authentication configuration setup correctly!")

@click.group()
@click.pass_context
def config(ctx):
    '''
    Group of commands to manage the jiractl command line
    '''
    pass

@click.command(name="show")
@click.argument('key', required=False)
@click.pass_context
def show_config(ctx, key):
    '''
    Shows the current configuration file for JIRA communication and default values

    Args:
        key (str): the key to show
    '''
    configuration = read_configfile(ctx.obj['config_file_path'])
    configuration['apikey'] = "**********"
    if not key:
        rich.print(configuration)
    elif configuration.get(key):
        print(configuration[key])

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
    configuration = read_configfile(ctx.obj['config_file_path'])
    configuration[key] = value
    write_config_file(ctx.obj['config_file_path'], configuration)

@click.command(name='remove')
@click.option('--key', '-k', help="The key to be removed", required=True, prompt=True)
@click.pass_context
def remove_config(ctx, key):
    '''
    Removes a key from the configuration file

    Args:
        key (str): The key to be removed
    '''
    configuration = read_configfile(ctx.obj['config_file_path'])
    del configuration[key]
    write_config_file(ctx.obj['config_file_path'], configuration)

config.add_command(show_config)
config.add_command(set_config)
config.add_command(remove_config)

def read_configfile(config_file_path: str) -> dict:
    '''
    This function reads the contents of the config file for jiractl and dumps it as a dict for later use

    Args:
        config_file_path (string): path of the config file

    Returns:
        dict: dictionary with the configuration to run jiractl
    '''
    if not os.path.isfile(config_file_path):
        create_default_configfile()
    with open(config_file_path, 'r') as file_reader:
        config_dict = json.loads(file_reader.read())
    return config_dict

def create_default_configfile():
    app_dir = click.get_app_dir(APP_NAME)
    if not os.path.isdir(app_dir):
            os.mkdir(app_dir)
    config = {}
    write_config_file(os.path.join(app_dir, CONFIG_FILE), config)

def write_config_file(file_path, data):
    with open(file_path, 'w') as file_writer:
        file_writer.write(json.dumps(data))


jira.add_command(login)
jira.add_command(config)

for client in [method_name for method_name in dir(get)
               if callable(getattr(get, method_name))]:
    jira.add_command(getattr(get, client))

for client in [method_name for method_name in dir(update)
               if callable(getattr(update, method_name))]:
    jira.add_command(getattr(update, client))

for client in [method_name for method_name in dir(create)
               if callable(getattr(create, method_name))]:
    jira.add_command(getattr(create, client))
