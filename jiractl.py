import os
import click
import requests
import rich

import get
import update
import create
import config

from shared_functions import write_config_file, get_config

@click.group()
@click.pass_context
def jira(ctx):
    '''
    JIRA Command Line Interface
    '''
    
    if ctx.invoked_subcommand != 'login':
        try:
            config = get_config()
        except KeyError:
            rich.print("You should authenticate with 'jira login' first!")
        config['api_endpoint'] = config['endpoint'] + "/rest/api"
        [os.environ.setdefault(key, config[key]) for key in config if key not in ['app_dir', 'endpoint', 'config_file_path', 'authenticated', 'headers']]


@click.command()
@click.option('--apikey', '-k', help="API Key for the user authentication", required=True, prompt=True, hide_input=True)
@click.option('--endpoint', '-e', help="the URI of the Jira website for your company", required=True, prompt=True)
@click.pass_context
def login(ctx, apikey, endpoint):
    '''
    Setup of the authentication values for the JIRA Rest API
    '''
    config = get_config()
    headers = {"Authorization": f"Bearer " + apikey,
                                "Content-Type": "application/json"}
    request = requests.get(endpoint + '/rest/api/latest/myself', headers=headers)
    request.raise_for_status()
    current_user = request.json()
    write_config_file(config['config_file_path'], {'apikey': apikey,'endpoint': endpoint, 'current_user': current_user['key']})
    print("Authentication configuration setup correctly!")


jira.add_command(login)

def add_all_commands(group):
    for client in [method_name for method_name in dir(group)
                if callable(getattr(group, method_name))]:
        jira.add_command(getattr(group, client))

groups = [get, update, create, config]

for group in groups:
    add_all_commands(group)

if __name__ == '__main__':
    jira()