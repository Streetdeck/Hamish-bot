#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 30 Apr 2020 05:03
# @Author  : Hamish Shing Shing Chau
# @File    : edit.py
# @Software: PyCharm

import requests
import pywikibot
import urllib.request
import json

config_file = open('./siteconfig.json', 'r', encoding='utf-8').read()
print(config_file)
config_data = json.loads(config_file)
i = 0
flag = False
for task in config_data:
    if task['disabled']:
        flag = True
        break
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
            print(error('JSONDecodeError: {} content: {} url: {}'.format(e, repo_info_str, url)))
            sys.exit(1)
        new_sha = repo_info[0]['sha']
    if new_sha == old_sha:
        flag = True
        break
    if not flag:
        config_data[i]['sha'] = new_sha
        commit_info_url = 'https://api.github.com/repos/{0}/{1}/commits/{2}'.format(github_uid, repo, new_sha)
        commit_info_str = urllib.request.urlopen(commit_info_url).read().decode("utf8")
        try:
            commit_info = json.loads(commit_info_str)
        except json.decoder.JSONDecodeError as e:
            print(error('JSONDecodeError: {} content: {} url: {}'.format(e, commit_info_str, url)))
            sys.exit(1)
        langcode = task['langcode']
        family = task['family']
        site = pywikibot.Site(langcode, family)
        site.login()
        prefix = task['prefix']
        summary = 'Update to '
        summary += '[https://github.com/{0}/{1}/commit/{2}'.format(github_uid, repo, new_sha) + ' ' + new_sha[:7] + ']'
        summary += ': ' + commit_info['commit']['message']
        for file_path in commit_info['files']:
            print(file_path)
            base_page = pywikibot.Page(site, prefix + str(file_path))
            base_text = base_page.text
            source_url = 'https://raw.githubusercontent.com/{0}/{1}/{2}/{3}'.format(github_uid, repo, branch, file_path)
            source_text = urllib.request.urlopen(source_url).read().decode('utf8')
            base_page.text = source_text
            pywikibot.showDiff(base_text, base_page.text)
            record_page.save(summary=summary, minor=False)
        config_file.write(config_data)
        config_file.close()
        php_text = "\"<?php if(isset($_SERVER[\'HTTP_X_GITHUB_EVENT\'])) { `cd ~/Hamish-bot/userjs-update " \
                   "&& python3 edit.py`; } ?>"
        php_file = open('~/public_html/git-pull.php', 'w', encoding='utf-8')
        php_file.write(php_text)
        php_file.close()
