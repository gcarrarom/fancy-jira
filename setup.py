from setuptools import setup, find_packages

setup(
    name='fancy-jira',
    version='0.0.3',
    author='Gui Martins',
    url='https://fancywhale.ca/',
    author_email='gmartins@fancywhale.ca',
    packages=find_packages(),
    include_package_data=True,
    py_modules=['jiractl'],
    install_requires=[
        'click',
        'requests',
        'rich',
        'PyYAML',
        'tabulate'
    ],
    entry_points='''
        [console_scripts]
        jira=jiractl:jira
    ''',
)
