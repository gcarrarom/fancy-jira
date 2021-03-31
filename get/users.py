import click
import requests
import json
import yaml

from rich import print as rprint
from rich.table import Table
from rich.console import Console

@click.command()
@click.argument('username', required=True)
@click.option('--output', '-o', help="The type of output", default="table", type=click.Choice(['yaml', 'json', 'table']))
@click.pass_context
def users(ctx, output, username):
    #print(f"Going here: {ctx.obj['api_endpoint']}/latest/user/search?username={username}")
    results = requests.get(f"{ctx.obj['api_endpoint']}/2/user/search?username={username}", headers=ctx.obj['headers'])
    results.raise_for_status()
    users_list = results.json()
    if output == 'json':
        print(json.dumps(users_list))
    elif output == 'table':
        console = Console()
        table = Table()
        table.add_column("USER ID", justify='left')
        table.add_column("DISPLAY NAME", justify='left')
        table.add_column("USER EMAIL", justify='left')
        for user in users_list:
            table.add_row(f"{user['key']} ", f"{user['displayName']} ", f"{user['emailAddress']} ")
        console.print(table)
    elif output == 'yaml':
        rprint(yaml.dump_all(users_list))