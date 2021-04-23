import click
import os
import json

def get_headers(config):
    return {"Authorization": f"Bearer {config.get('apikey')}",
            "Content-Type": "application/json", 
            "Accept": "application/json"}

def get_config():
    app_name = '.jiractl'
    config_file = 'config.json'
    app_dir = click.get_app_dir(app_name)
    config_file_path = os.path.join(app_dir, config_file)
    config = read_configfile(config_file_path)
    config['authenticated'] = True
    config['headers'] = get_headers(config)
    config['api_endpoint'] = config.get('endpoint', "") + "/rest/api"
    config['app_dir'] = app_dir
    config['config_file_path'] = config_file_path
    return config

def read_configfile(config_file_path: str) -> dict:
    '''
    This function reads the contents of the config file for jiractl and dumps it as a dict for later use

    Args:
        config_file_path (string): path of the config file

    Returns:
        dict: dictionary with the configuration to run jiractl
    '''
    if not os.path.isfile(config_file_path):
        create_default_configfile()
    with open(config_file_path, 'r') as file_reader:
        config_dict = json.loads(file_reader.read())
    return config_dict

def create_default_configfile():
    app_name = '.jiractl'
    config_file = 'config.json'
    app_dir = click.get_app_dir(app_name)
    if not os.path.isdir(app_dir):
            os.mkdir(app_dir)
    config = {}
    write_config_file(os.path.join(app_dir, config_file), config)

def write_config_file(file_path, data):
    if data.get('headers'): del data['headers']
    if data.get('app_dir'): del data['app_dir']
    if data.get('config_file_path'): del data['config_file_path']
    if data.get('authenticated'): del data['authenticated']
    with open(file_path, 'w') as file_writer:
        file_writer.write(json.dumps(data))