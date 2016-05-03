#!/usr/bin/env python

import subprocess
import requests
import syslog
import sys
import os

backup_dir = os.environ.get('GITHUB_BACKUP_DIR', '/tmp/github_backup')
token = os.environ.get('GITHUB_TOKEN')
urls = [
    'https://api.github.com/orgs/lemonde/repos',
    'https://api.github.com/user/repos'
]


def main():
    if not os.path.isdir(backup_dir):
        sys.exit("%s directory doesn't exist" % backup_dir)

    for url in urls:
        _backup(r=_repos(url))


def _repos(url):
    return requests.get(
        url,
        headers={'Authorization': 'token %s' % token}
    )


def _backup(r):
    for repository in r.json():
        url = repository['html_url'].replace(
            'github.com',
            '%s:x-oauth-basic@github.com' % token
        )
        split_url = url.split('/')
        dirname = split_url[-1]
        os.chdir(backup_dir)

        if not os.path.isdir('%s/%s' % (backup_dir, dirname)):
            try:
                subprocess.call("git clone --mirror %s %s" % (url, dirname), shell=True)
                syslog.syslog(syslog.LOG_INFO, "Git clone OK : %s" % dirname)
            except:
                syslog.syslog(syslog.LOG_CRIT, "Git clone FAILED : %s" % dirname)
                pass

        try:
            os.chdir("%s/%s" % (backup_dir, dirname))
            subprocess.call('git remote update &>/dev/null', shell=True)
            syslog.syslog(syslog.LOG_INFO, "Git remote update OK : %s" % dirname)
        except:
            syslog.syslog(syslog.LOG_CRIT, "Git remote update FAILED : %s" % dirname)


if __name__ == "__main__":
    main()
