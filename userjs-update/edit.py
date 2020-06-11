#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 30 Apr 2020 05:03
# @Author  : Hamish Shing Shing Chau
# @File    : edit.py
# @Software: PyCharm

import pywikibot
import urllib.request
import json
import re
import sys
sys.path.append('/data/project/shared/pywikibot/stable')
sys.path.append('/data/project/shared/pywikibot/stable/scripts')
sys.path.append('/data/project/hamishbot/www/python/venv/lib/python3.7/site-packages')
from config import config_page_name # pylint: disable=E0611,W0614

config_site = pywikibot.Site('zh', 'wikipedia')
config_page = pywikibot.Page(config_site, config_page_name)
config_text = config_page.text
old_config_text = config_page.text
config_data = json.loads(config_text)
i = 0

for task in config_data:
    flag = False
    if task['disabled']:
        flag = True
        continue
    if not flag:
        repo = task['repo']
        branch = task['branch']
        old_sha = task['sha']
        github_uid = task['github_uid']
        repo_info_url = 'https://api.github.com/repos/{0}/{1}/commits?sha={2}'.format(github_uid, repo, branch)
        repo_info_str = urllib.request.urlopen(repo_info_url).read().decode("utf8")
        try:
            repo_info = json.loads(repo_info_str)
        except json.decoder.JSONDecodeError as e:
            print('JSONDecodeError: {} content: {} url: {}'.format(e, repo_info_str, repo_info_url))
            sys.exit(1)
        new_sha = repo_info[0]['sha']
    if new_sha == old_sha:
        flag = True
        continue
    if not flag:
        config_text = re.sub(old_sha, new_sha, config_text)
        commit_info_url = 'https://api.github.com/repos/{0}/{1}/commits/{2}'.format(github_uid, repo, new_sha)
        commit_info_str = urllib.request.urlopen(commit_info_url).read().decode("utf8")
        try:
            commit_info = json.loads(commit_info_str)
        except json.decoder.JSONDecodeError as e:
            print('JSONDecodeError: {} content: {} url: {}'.format(e, commit_info_str, commit_info_url))
            sys.exit(1)
        langcode = task['langcode']
        family = task['family']
        site = pywikibot.Site(langcode, family)
        site.login()
        prefix = task['prefix']
        summary = 'Update to ' + new_sha[:7] + ': ' + commit_info['commit']['message']
        for file in commit_info['files']:
            file_path = file['filename']
            if "modules" in file_path:
                print(file_path)
                base_page = pywikibot.Page(site, prefix + str(file_path))
                base_text = base_page.text
                source_url = 'https://raw.githubusercontent.com/{0}/{1}/{2}/{3}'.format(github_uid, repo, branch, file_path)
                source_text = urllib.request.urlopen(source_url).read().decode('utf8')
                base_page.text = source_text
                pywikibot.showDiff(base_text, base_page.text)
                base_page.save(summary=summary, minor=False)
            else:
                continue
config_page.text = config_text
pywikibot.showDiff(old_config_text, config_page.text)
config_page.save(summary='Update', minor=False)
