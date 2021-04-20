import click
import requests
import json
import yaml
from shared_functions import get_config

from rich import print as rprint
from tabulate import tabulate

@click.command()
@click.argument('username', required=True)
@click.option('--output', '-o', help="The type of output", default="table", type=click.Choice(['yaml', 'json', 'table']))
@click.pass_context
def users(ctx, output, username):
    config = get_config()
    #print(f"Going here: {ctx.obj['api_endpoint']}/latest/user/search?username={username}")
    results = requests.get(f"{config['api_endpoint']}/2/user/search?username={username}", headers=config['headers'])
    results.raise_for_status()
    users_list = results.json()
    if output == 'json':
        print(json.dumps(users_list))
    elif output == 'table':
        table = []
        table_headers = []
        table_headers.append("USER ID")
        table_headers.append("DISPLAY NAME")
        table_headers.append("USER EMAIL")
        for user in users_list:
            table.append([user['key'], user['displayName'], user['emailAddress']])
        print(tabulate(table, headers=table_headers))
    elif output == 'yaml':
        rprint(yaml.dump_all(users_list))