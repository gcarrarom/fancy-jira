from setuptools import setup, find_packages

with open("./README.md", 'r') as fr:
    readme_file = fr.read()

setup(
    name='fancy-jira',
    version='0.1.1',
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
    long_description=readme_file
)
