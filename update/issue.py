import click
import requests

@click.command()
@click.argument('issue')
@click.option('--story-points', '-s', help="Sets the story points for the jira issue")
@click.pass_context
def issue(ctx, issue, story_points):
    body = {'fields':{}}

    if story_points:
        body['fields']["customfield_10002"] = float(story_points)

    request = requests.put(ctx.obj['api_endpoint'] + '/latest/issue/' + issue, json=body, headers=ctx.obj['headers'])

    request.raise_for_status()

