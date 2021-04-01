import click
import requests
import json
import yaml
import re
import os

from rich import print as rprint
from rich.table import Table
from rich.console import Console

def get_issue_order(issue):
    status = issue['fields']['status']['statusCategory']['name']
    if status == "To Do": 
        return 10
    if status == "In Progress":
        return 5
    else:
        return 1

@click.command()
@click.option('--user', '-u', help='ID of the user to search issues for', default=lambda: os.environ.get('current_user'), show_default="configured 'current_user'")
@click.option('--project', '-p', help="Which project to search for the issues", default=lambda: os.environ.get('project'), show_default="configured 'project'")
@click.option('--scrum-team', '-t', help="The scrum team assigned for the issues", default=lambda: os.environ.get('scrum_team'), show_default="configured 'scrum_team'")
@click.option('--sprint', '-s', help="Which sprint to search for the issues", default=lambda: os.environ.get('sprint'), show_default="configured 'sprint'")
@click.option('--output', '-o', help="The type of output", default="table", type=click.Choice(['yaml', 'json', 'table']))
@click.option('--show-query', help="Shows the query to be used", is_flag=True)
@click.option('--all-users', help='Query all users', is_flag=True, default=False)
@click.option('--all-projects', '-A', help='Query all projects', is_flag=True, default=False)
@click.option('--all-sprints', help="Query all sprints", is_flag=True, default=False)
@click.option('--all-scrum-teams', help="Query all scrum teams", is_flag=True, default=False)
@click.option('--include-closed', help="Includes the closed items", is_flag=True)
@click.option('--show-story-points', help="Shows the story points of all issues", is_flag=True)
@click.pass_context
def issues(ctx, output, user, include_closed, show_query, project, all_projects, sprint, all_sprints, show_story_points, scrum_team, all_scrum_teams, all_users):
    body = {'jql':""}
    first = True
    # Query for assignee current user if user is not set
    if not all_users:
        body['jql'] += "assignee = " + user
        first = False

    # Query only for status not Closed if flag include_closed is not set
    if not include_closed:
        if not first:
            body['jql'] += " AND "
        else: 
            first = False
        body['jql'] += "status != Closed"

    # Query for project set in options or default project. Query everything if not set
    if project and not all_projects:
        if not first:
            body['jql'] += " AND "
        else: 
            first = False
        body['jql'] += "project = " + project
    else:
        all_projects = True

    # Query for sprint set in options or default sprint. Query everything if not set
    if not all_sprints and sprint:
        if not first:
            body['jql'] += " AND "
        else: 
            first = False
        body['jql'] += "Sprint = '" + sprint + "'"
    else:
        all_sprints = True

    # Query for scrum team set in options or default scrum team. Query everything if not set
    if scrum_team and not all_scrum_teams:
        if not first:
            body['jql'] += " AND "
        else: 
            first = False
        body['jql'] += "'Scrum Teams' = '" + scrum_team + "'"
    else: 
        all_scrum_teams = True

    if show_query: rprint(body['jql'])
    
    request = requests.post(ctx.obj['api_endpoint'] + '/latest/search', json=body, headers=ctx.obj['headers'])
    request.raise_for_status()
    issues_returned = request.json()['issues']
    if output == 'json':
        print(json.dumps(issues_returned))
    elif output == 'yaml':
        rprint(yaml.dump(issues_returned))
    else: 
        console = Console()
        table = Table()
        if all_projects: table.add_column("PROJECT", justify='left')
        table.add_column("ISSUE", justify='left')
        table.add_column("SUMMARY", justify='left')
        table.add_column("STATUS", justify='left')
        table.add_column("ASSIGNEE", justify='left')
        if all_sprints: table.add_column("SPRINT", justify='left')
        if show_story_points: table.add_column("STORY POINTS", justify='left')
        issues_returned.sort(key=get_issue_order)
        for issue in issues_returned:
            to_add = []
            if all_projects: to_add.append(issue['fields']['project']['key'])
            to_add.append(issue['key'])
            to_add.append(issue['fields']['summary'])
            to_add.append(issue['fields']['status']['statusCategory']['name'])
            if issue['fields'].get('assignee'): to_add.append(issue['fields']['assignee']['displayName'] + "(" + issue['fields']['assignee']['key'] + ")")
            if issue['fields'].get('customfield_12800') and all_sprints: 
                to_add.append(re.findall('(?:name=)(.*)(?:,startDate)', issue['fields']['customfield_12800'][0])[0])
            if show_story_points:
                to_add.append(str(issue['fields'].get('customfield_10002')))
            table.add_row(*to_add)
        console.print(table)


