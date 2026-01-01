# -*- coding: utf-8 -*-
from datetime import timezone
import argparse
import os
import re
from github import Github, Auth, GithubException
from datetime import timezone
from marko.ext.gfm import gfm as marko
from feedgen.feed import FeedGenerator
from lxml.etree import CDATA

# 文艺风 Header
MD_HEAD = """## 不属于任何人，也不拥有任何人，减少期待，好好生活，此程山高路远，我留给自己。 
"""

BACKUP_DIR = "BACKUP"
ANCHOR_NUMBER = 5
TOP_ISSUES_LABELS = ["Top"]
TODO_ISSUES_LABELS = ["TODO"]
FRIENDS_LABELS = ["Friends"]
IGNORE_LABELS = FRIENDS_LABELS + TOP_ISSUES_LABELS + TODO_ISSUES_LABELS

FRIENDS_TABLE_HEAD = "| Name | Link | Desc | \n | ---- | ---- | ---- |\n"
FRIENDS_TABLE_TEMPLATE = "| {name} | {link} | {desc} |\n"
FRIENDS_INFO_DICT = {"名字": "", "链接": "", "描述": ""}

def get_me(user):
    return user.get_user().login

def is_me(issue, me):
    return issue.user.login == me

def is_hearted_by_me(comment, me):
    reactions = list(comment.get_reactions())
    for r in reactions:
        if r.content == "heart" and r.user.login == me:
            return True
    return False

def _make_friend_table_string(s):
    info_dict = FRIENDS_INFO_DICT.copy()
    try:
        string_list = [l for l in s.splitlines() if l and not l.isspace()]
        for l in string_list:
            string_info_list = re.split("：|:", l) # 同时兼容中英文冒号
            if len(string_info_list) < 2:
                continue
            info_dict[string_info_list[0].strip()] = string_info_list[1].strip()
        return FRIENDS_TABLE_TEMPLATE.format(
            name=info_dict["名字"], link=info_dict["链接"], desc=info_dict["描述"]
        )
    except Exception as e:
        print(f"Friend Parse Error: {e}")
        return ""

def _valid_xml_char_ordinal(c):
    codepoint = ord(c)
    return (0x20 <= codepoint <= 0xD7FF or codepoint in (0x9, 0xA, 0xD) or
            0xE000 <= codepoint <= 0xFFFD or 0x10000 <= codepoint <= 0x10FFFF)

def format_time(time):
    return time.strftime("%Y-%m-%d")

def add_issue_info(issue, md):
    time = format_time(issue.created_at)
    md.write(f"- [{issue.title}]({issue.html_url}) -- {time}\n")

def add_md_recent(repo, md_path, me, limit=5):
    with open(md_path, "a+", encoding="utf-8") as md:
        md.write("## 最近更新\n")
        issues = repo.get_issues(state="open")
        count = 0
        for issue in issues:
            if is_me(issue, me) and not issue.pull_request:
                add_issue_info(issue, md)
                count += 1
                if count >= limit: break

def add_md_header(md_path, repo_name):
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(MD_HEAD)

def generate_rss_feed(repo, filename, me):
    fg = FeedGenerator()
    fg.id(repo.html_url)
    fg.title(f"{me}'s Blog")
    fg.author({'name': me})
    fg.link(href=repo.html_url, rel='alternate')
    
    for issue in repo.get_issues(state="open"):
        if not issue.body or not is_me(issue, me) or issue.pull_request:
            continue
        fe = fg.add_entry()
        fe.id(issue.html_url)
        fe.title(issue.title)
        fe.link(href=issue.html_url)
        
        if issue.created_at.tzinfo is None:
            published_time = issue.created_at.replace(tzinfo=timezone.utc)
        else:
            published_time = issue.created_at
        fe.published(published_time)
    
        content = "".join(c for c in issue.body if _valid_xml_char_ordinal(c))
        fe.content(CDATA(marko.convert(content)), type="html")
    fg.atom_file(filename)

def save_issue(issue, me, dir_name):
    # 替换标题中的非法文件名字符
    safe_title = re.sub(r'[\\/:*?"<>|]', '_', issue.title)
    md_name = os.path.join(dir_name, f"{issue.number}_{safe_title}.md")
    with open(md_name, "w", encoding="utf-8") as f:
        f.write(f"# [{issue.title}]({issue.html_url})\n\n{issue.body}")

def main(token, repo_name, issue_number=None):
   
    auth = Auth.Token(token)
    gh = Github(auth=auth)
    me = os.getenv("GITHUB_NAME")
    if not me:
        try:
            me = gh.get_user().login
        except Exception:
            # 如果是 GITHUB_TOKEN 可能无法获取 get_user，直接通过 repo 路径解析
            me = repo_name.split('/')[0]
    
    repo = gh.get_repo(repo_name)
    
    add_md_header("README.md", repo_name)
    add_md_recent(repo, "README.md", me)
    generate_rss_feed(repo, "feed.xml", me)
    
    if not os.path.exists(BACKUP_DIR):
        os.mkdir(BACKUP_DIR)
        
    for issue in repo.get_issues(state="open"):
        if is_me(issue, me) and not issue.pull_request:
            save_issue(issue, me, BACKUP_DIR)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token")
    parser.add_argument("repo_name")
    parser.add_argument("--issue_number", default=None)
    args = parser.parse_args()
    main(args.github_token, args.repo_name, args.issue_number)
