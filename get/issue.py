import click
import requests
import json
import yaml
from shared_functions import get_config

from rich import print as rprint

@click.command()
@click.argument('issue_id')
@click.option('--output', '-o', help="The type of output", default="json", type=click.Choice(['yaml', 'json', 'table']))
@click.pass_context
def issue(ctx, issue_id, output):
    config = get_config()
    request = requests.get(config['api_endpoint'] + '/latest/issue/' + issue_id, headers=config['headers'])
    request.raise_for_status()
    issue_returned = request.json()
    if output == 'json':
        print(json.dumps(issue_returned))
    elif output == 'yaml':
        rprint(yaml.dump(issue_returned))