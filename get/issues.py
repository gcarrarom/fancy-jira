import click
import requests
import json
import yaml
import re

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
@click.option('--output', '-o', help="The type of output", default="table", type=click.Choice(['yaml', 'json', 'table']))
@click.option('--user', '-u', help='ID of the user to search issues for', default=False)
@click.option('--include-closed', help="Includes the closed items", is_flag=True)
@click.option('--show-query', help="Shows the query to be used", is_flag=True)
@click.option('--project', '-p', help="Which project to search for the issues", default=False)
@click.option('--all-projects', '-A', help='Query all projects', is_flag=True, default=False)
@click.option('--sprint', '-s', help="Which sprint to search for the issues", default=False)
@click.option('--all-sprints', help="Query all sprints", is_flag=True, default=False)
@click.pass_context
def issues(ctx, output, user, include_closed, show_query, project, all_projects, sprint, all_sprints):
    body = {}
    # Query for assignee current user if user is not set
    body['jql'] = "assignee = " 
    body['jql'] += ctx.obj['current_user'] if not user else user

    # Query only for status not Closed if flag include_closed is not set
    body['jql'] += " AND status != Closed" if not include_closed else ""

    # Query for project set in options or default project. Query everything if not set
    if (project or ctx.obj.get('project')) and not all_projects:
        body['jql'] += " AND project = " + project if project else " AND project = " + ctx.obj['project']
    else:
        all_projects = True

    if (sprint or ctx.obj.get('sprint')) and not all_sprints:
        body['jql'] += " AND Sprint = '" + sprint + "'" if sprint else " AND Sprint = '" + ctx.obj['sprint'] + "'"
    else: 
        all_sprints = True

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
        issues_returned.sort(key=get_issue_order)
        for issue in issues_returned:
            to_add = []
            if all_projects: to_add.append(issue['fields']['project']['key'])
            to_add.append(issue['key'])
            to_add.append(issue['fields']['summary'])
            to_add.append(issue['fields']['status']['statusCategory']['name'])
            to_add.append(issue['fields']['assignee']['displayName'] + "(" + issue['fields']['assignee']['key'] + ")")
            if issue['fields'].get('customfield_12800') and all_sprints: 
                to_add.append(re.findall('(?:name=)(.*)(?:,startDate)', issue['fields']['customfield_12800'][0])[0])
            table.add_row(*to_add)
        console.print(table)
