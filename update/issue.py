import click
import requests
from shared_functions import get_config


@click.command()
@click.argument('issue_id')
@click.option('--story-points', '-s', help="Sets the story points for the jira issue")
@click.pass_context
def issue(ctx, issue_id, story_points):
    config = get_config()
    body = {'fields':{}}

    if story_points:
        body['fields']["customfield_10002"] = float(story_points)

    request = requests.put(config['api_endpoint'] + '/latest/issue/' + issue_id, json=body, headers=config['headers'])

    request.raise_for_status()

