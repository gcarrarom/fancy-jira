import click
import requests
from get.issues import get_issues
from shared_functions import get_config


def get_issues_autocomp(ctx, args, incomplete):
    config = get_config()

    returned = get_issues("python", config.get('current_user'), False, False, config.get('project'), False, config.get('sprint'),
                          False, False, config.get('scrum_team'), False, False, False)
    
    return [(issue['key'],issue['fields']['summary']) for issue in returned if incomplete in issue['fields']['summary'] or incomplete in issue['key']]

@click.command()
@click.argument('issue', type=click.STRING, autocompletion=get_issues_autocomp)
@click.option('--comment', '-c', help="Comment text to add", type=str, required=True)
@click.pass_context
def comment(ctx, issue, comment):
    config = get_config()
    body = {
        "body": comment
    }
    request = requests.post(config['api_endpoint'] + '/latest/issue/' + issue + '/comment', json=body, headers=config['headers'])
    try:
        request.raise_for_status()
    except Exception as exc:
        click.echo(request.text)
        raise exc
        
    click.echo("Comment for issue '" + issue + "' created successfully!")


if __name__ == '__main__':
    get_issues_autocomp(None, None, None)