import click
import requests
import json
import yaml
import re
import os
from shared_functions import get_config

from rich import print as rprint
from tabulate import tabulate

def get_issue_order(issue):
    status = issue['fields']['status']['statusCategory']['name']
    if status == "To Do": 
        return 10
    if status == "In Progress":
        return 5
    else:
        return 1

@click.command()
@click.option('--user', '-u', help='ID of the user to search issues for', default=lambda: os.environ.get('current_user', False), show_default="configured 'current_user'")
@click.option('--project', '-p', help="Which project to search for the issues", default=lambda: os.environ.get('project', False), show_default="configured 'project'")
@click.option('--scrum-team', '-t', help="The scrum team assigned for the issues", default=lambda: os.environ.get('scrum_team', False), show_default="configured 'scrum_team'")
@click.option('--sprint', '-s', help="Which sprint to search for the issues", default=lambda: os.environ.get('sprint', False), show_default="configured 'sprint'")
@click.option('--output', '-o', help="The type of output", default="table", type=click.Choice(['yaml', 'json', 'table']))
@click.option('--show-query', help="Shows the query to be used", is_flag=True)
@click.option('--all-users', help='Query all users', is_flag=True, default=False)
@click.option('--all-projects', '-A', help='Query all projects', is_flag=True, default=False)
@click.option('--all-sprints', help="Query all sprints", is_flag=True, default=False)
@click.option('--all-scrum-teams', help="Query all scrum teams", is_flag=True, default=False)
@click.option('--include-closed', help="Includes the closed items", is_flag=True)
@click.option('--show-story-points', help="Shows the story points of all issues", is_flag=True)
@click.option('--show-url', help="Shows the url of the Jira issue rather than the ID only", is_flag=True)
@click.pass_context
def issues(ctx, output, user, include_closed, show_query, project, 
           all_projects, sprint, all_sprints, show_story_points, 
           scrum_team, all_scrum_teams, all_users, show_url):
    get_issues(output, user, include_closed, show_query, project, 
               all_projects, sprint, all_sprints, show_story_points, 
               scrum_team, all_scrum_teams, all_users, show_url)

def query_build(query, query_string):
    if not query:
        return query_string
    else:
        return query + ' AND ' + query_string

def get_issues(output, user, include_closed, show_query, project, 
               all_projects, sprint, all_sprints, show_story_points, 
               scrum_team, all_scrum_teams, all_users, show_url):
    config = get_config()
    body = {'jql':""}

    query = None
    # Query for assignee current user if user is not set
    query = query_build(query, "assignee = " + user) if not all_users else query

    # Query only for status not Closed if flag include_closed is not set
    query = query_build(query, "status != Closed") if not include_closed else query

    # Query for project set in options or default project. Query everything if not set
    if not project:
        all_projects = True
    query = query_build(query, "project = " + project) if not all_projects else query

    # Query for sprint set in options or default sprint. Query everything if not set
    if not sprint:
        all_sprints = True
    query = query_build(query, "Sprint = '" + sprint + "'") if not all_sprints else query

    # Query for scrum team set in options or default scrum team. Query everything if not set
    if not scrum_team:
        all_scrum_teams = True
    query = query_build(query, "'Scrum Teams' = '" + scrum_team + "'") if not all_scrum_teams else query
    body['jql'] = query
    if show_query: 
        rprint(query)
    
    request = requests.post(config['api_endpoint'] + '/latest/search', json=body, headers=config['headers'])
    request.raise_for_status()
    issues_returned = request.json()['issues']
    if output == 'python':
        return issues_returned
    elif output == 'json':
        print(json.dumps(issues_returned))
    elif output == 'yaml':
        rprint(yaml.dump(issues_returned))
    else: 
        table = []
        table_headers = []
        if all_projects: table_headers.append("PROJECT")
        table_headers.append("ISSUE")
        table_headers.append("SUMMARY")
        table_headers.append("STATUS")
        table_headers.append("ASSIGNEE")
        if all_sprints: table_headers.append("SPRINT")
        if show_story_points: table_headers.append("STORY POINTS")
        issues_returned.sort(key=get_issue_order)
        for issue in issues_returned:
            to_add = []
            if all_projects: to_add.append(issue['fields']['project']['key'])
            to_add.append(issue['key'] if not show_url else "https://jira.finastra.com/browse/" + issue['key'])
            to_add.append(issue['fields']['summary'])
            to_add.append(issue['fields']['status']['statusCategory']['name'])
            if issue['fields'].get('assignee'): to_add.append(issue['fields']['assignee']['displayName'] + "(" + issue['fields']['assignee']['key'] + ")")
            if issue['fields'].get('customfield_12800') and all_sprints: 
                to_add.append(re.findall('(?:name=)(.*)(?:,startDate)', issue['fields']['customfield_12800'][0])[0])
            if show_story_points:
                to_add.append(str(issue['fields'].get('customfield_10002')))
            table.append(to_add)
        print(tabulate(table, headers=table_headers))
