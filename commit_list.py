"""
this program takes the apikey and username from the config file 
and compiles a list of commits authored by that user.

currently this program is time and api access intensive, and does not store partial nor complete results
but writes directly to stdout
"""

from configparser import ConfigParser
import github
import logging

logging.basicConfig(level=logging.INFO)

APIKEY: str
USERNAME : str

def authenticate():
    global APIKEY, USERNAME
    config = ConfigParser()
    config.read('config.ini')
    config['DEFAULT'] = {'apikey':'', 'username':''}
    APIKEY = config['commit_list']['apikey']
    USERNAME = config['commit_list']['username']
    if APIKEY:
        # authenticate with api key
        g = github.Github(APIKEY)
    else:
        # authenticate with username and password'
        logging.warning('no api key provided, please login with github credentials')
        import getpass
        USERNAME = input("username > ")
        g = github.Github(USERNAME, getpass.getpass())
    try:
        lim=g.get_rate_limit()
    except github.BadCredentialsException:
        logging.fatal('invalid credentials')
        exit(1)
    else:
        if lim.core.limit == 60:
            logging.fatal('unauthenticated user')
            exit(1)
        if lim.core.remaining < 2000:
            logging.fatal('insufficient api calls remaining')
            logging.fatal(f'api calls reset on {lim.core.reset}.')
            exit()
    return g

g: github.Github = authenticate()

commits = list()

commit_queue = list()


def get_branch_commits():
    for repo in g.get_organization("R2D2-2019").get_repos():
        for branch in repo.get_branches():
            print(branch)
            if not branch.commit:
                logging.warning(branch.name + ' in ' + repo.name + ' has no commits')
            if branch.commit not in commit_queue:
                commit_queue.append(branch.commit)

def get_parents():
    while commit_queue:
        commit = commit_queue.pop()
        if commit in commits:
            continue
        commits.append(commit)
        for commit_parent in commit.parents:
            if commit_parent not in commits and commit_parent not in commit_queue:
                commit_queue.append(commit_parent)

if __name__ == "__main__":
    get_branch_commits()
    get_parents()

    filtered = list(filter((lambda commit: commit.author.name == USERNAME if commit.author else False), commits))

    filtered.sort(key=(lambda commit: commit.commit.author.date))

    last_weeknum = 0
    for commit in filtered:
        weeknum = commit.commit.author.date.isocalendar()[1]
        if weeknum > last_weeknum:
            last_weeknum = weeknum
            print('Year-week', weeknum)
        print(commit.html_url)
