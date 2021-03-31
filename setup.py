from setuptools import setup, find_packages

setup(
    name='jiractl',
    version='0.0.1',
    author='Gui Martins',
    packages=find_packages(),
    include_package_data=True,
    py_modules=['jiractl'],
    install_requires=[
        'Click',
        'requests',
        'rich'
    ],
    entry_points='''
        [console_scripts]
        jira=jiractl:jira
    ''',
)
