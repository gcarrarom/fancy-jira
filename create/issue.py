import click
import os
import requests
from shared_functions import get_config

@click.command()
@click.option('--summary', '-s', help="the summary of the issue to be created", prompt=True, required=True)
@click.option('--scenario', help='Scenario of the Issue', prompt=True, required=True)
@click.option('--acceptance', '-a', help='Criteria of the acceptance of this issue', prompt=True, required=True)
@click.option('--description', '-d', help="Description of the issue to be created", prompt=True, required=True)
@click.option('--epic', '-e', help="Epic to attach this issue to")
@click.option('--label', '-l', help='Label to be added to the issue')
@click.option('--user', '-u', help='ID of the user to assign the issue', default=lambda: os.environ.get('current_user'), show_default="configured 'current_user'")
@click.option('--project', '-p', help="Project to assign this issue to", default=lambda: os.environ.get('project'), show_default="configured 'project'")
@click.option('--scrum-team', '-t', help="Scrum team to assign this issue to", default=lambda: os.environ.get('scrum_team'), show_default="configured 'scrum_team'")
@click.option('--sprint', help="Sprint to assign this issue to", default=lambda: os.environ.get('sprint'), show_default="configured 'sprint'")
@click.option('--issue-type', help="Type of the issue to be created", type=click.Choice(['epic', 'Story', 'bug']), default='Story', show_default='Story')
@click.pass_context
def issue(ctx, summary, scenario, acceptance, description, epic, label, user, project, scrum_team, sprint, issue_type):
    config = get_config()
    body = {
        "fields":{'summary': summary,
                  'description': description,
                  'issuetype': {'name': issue_type},
                  'customfield_10117': scenario,
                  'customfield_10118': acceptance}
    }
    if epic: body['fields']['customfield_15702'] = epic
    if user: body['fields']['assignee'] = {'name':user}
    if project: body['fields']['project'] = {'key': project}
    if scrum_team: body['fields']['customfield_16100'] = [{'value': scrum_team}]

    if sprint: 
        # Searching for the sprint
        request = requests.get('https://jira.finastra.com/rest/greenhopper/1.0/sprint/picker?query=' + sprint, headers=config['headers'])
        request.raise_for_status()
        sprints_suggestions = request.json()['suggestions']
        if len(sprints_suggestions) != 1:
            raise Exception("There is more than 1 sprint suggested by the name '" + sprint + "'! Please check the name of your sprint!")
        body['fields']['customfield_12800'] = sprints_suggestions[0]['id']

    if label: body['fields']['labels'] = [label]
    

    request = requests.post(config['api_endpoint'] + '/latest/issue', json=body, headers=config['headers'])

    try:
        request.raise_for_status()
    except Exception as exc:
        click.echo(request.text)
        raise exc
        
    issue_created = request.json()
    click.echo("Issue '" + issue_created['key'] + "' created successfully!")