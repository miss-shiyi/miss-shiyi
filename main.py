# -*- coding: utf-8 -*-
import argparse
import os
import re
from datetime import timezone
from github import Github, Auth
from marko.ext.gfm import gfm as marko
from feedgen.feed import FeedGenerator
from lxml.etree import CDATA

# --- 文艺风配置 ---
MD_HEAD = """# 🌙 miss-shiyi's Digital Garden
> **"不属于任何人，也不拥有任何人，减少期待，好好生活，此程山高路远，我留给自己。"**
---
"""

BACKUP_DIR = "BACKUP"
ANCHOR_NUMBER = 5
TOP_ISSUES_LABELS = ["Top"]
TODO_ISSUES_LABELS = ["TODO"]
FRIENDS_LABELS = ["Friends"]
# 忽略列表，这些标签不会单独作为分类显示
IGNORE_LABELS = FRIENDS_LABELS + TOP_ISSUES_LABELS + TODO_ISSUES_LABELS + ["bug", "help wanted", "invalid", "question"]

# 分类图标映射
LABEL_ICONS = {"Python": "🐍", "Life": "🌱", "Automation": "🤖", "Code": "💻", "Thoughts": "💡"}

def get_me(gh):
    me = os.getenv("GITHUB_NAME")
    return me if me else gh.get_user().login

def is_me(issue, me):
    return issue.user.login == me

def format_time(time):
    return time.strftime("%Y-%m-%d")

def _valid_xml_char_ordinal(c):
    codepoint = ord(c)
    return (0x20 <= codepoint <= 0xD7FF or codepoint in (0x9, 0xA, 0xD) or
            0xE000 <= codepoint <= 0xFFFD or 0x10000 <= codepoint <= 0x10FFFF)

# --- 核心分类逻辑 (参考你原来的写法) ---
def add_md_label(repo, md_path, me):
    labels = repo.get_labels()
    sidebar_content = ["* [🏠 首页](README.md)\n\n"]
    
    with open(md_path, "a+", encoding="utf-8") as md:
        md.write("## 📂 文章分类\n\n")
        
        for label in labels:
            if label.name in IGNORE_LABELS:
                continue

            # 获取该标签下的 Issue (参考你原来的 get_issues_from_label)
            issues = repo.get_issues(labels=[label], state="open")
            
            if issues.totalCount:
                icon = LABEL_ICONS.get(label.name, "🔖")
                md.write(f"### {icon} {label.name}\n")
                sidebar_content.append(f"* **{icon} {label.name}**\n")
                
                # 排序
                sorted_issues = sorted(issues, key=lambda x: x.created_at, reverse=True)
                
                count = 0
                for issue in sorted_issues:
                    if not is_me(issue, me) or issue.pull_request:
                        continue
                        
                    if count == ANCHOR_NUMBER:
                        md.write("<details><summary>显示更多</summary>\n\n")
                    
                    # 写入 README
                    time_str = format_time(issue.created_at)
                    md.write(f"- `[{time_str}]` [{issue.title}]({issue.html_url})\n")
                    
                    # 写入 侧边栏 (Docsify 专用)
                    safe_title = issue.title.replace(" ", ".")
                    sidebar_content.append(f"  * [{issue.title}](BACKUP/{issue.number}_{safe_title}.md)\n")
                    count += 1
                
                if count > ANCHOR_NUMBER:
                    md.write("\n</details>\n")
                md.write("\n")

    # 生成侧边栏文件
    with open("_sidebar.md", "w", encoding="utf-8") as sb:
        sb.writelines(sidebar_content)

def add_md_recent(repo, md_path, me, limit=5):
    with open(md_path, "a+", encoding="utf-8") as md:
        md.write("## 🕒 最近更新\n")
        issues = repo.get_issues(state="open", sort="updated")
        count = 0
        for issue in issues:
            if is_me(issue, me) and not issue.pull_request:
                time_str = format_time(issue.created_at)
                md.write(f"- `[{time_str}]` [{issue.title}]({issue.html_url})\n")
                count += 1
                if count >= limit: break
        md.write("\n---\n")

def generate_rss_feed(repo, filename, me):
    fg = FeedGenerator()
    fg.id(repo.html_url)
    fg.title(f"{me}'s Digital Garden")
    fg.link(href=repo.html_url, rel='alternate')
    for issue in repo.get_issues(state="open"):
        if not issue.body or not is_me(issue, me) or issue.pull_request:
            continue
        fe = fg.add_entry()
        fe.id(issue.html_url)
        fe.title(issue.title)
        fe.published(issue.created_at.replace(tzinfo=timezone.utc))
        body = "".join(c for c in issue.body if _valid_xml_char_ordinal(c))
        fe.content(CDATA(marko.convert(body)), type="html")
    fg.atom_file(filename)

def save_issue(issue, me, dir_name):
    # 保持你原来的命名习惯：编号_标题.md
    safe_title = issue.title.replace(" ", ".")
    md_name = os.path.join(dir_name, f"{issue.number}_{safe_title}.md")
    with open(md_name, "w", encoding="utf-8") as f:
        f.write(f"# [{issue.title}]({issue.html_url})\n\n{issue.body}")

def main(token, repo_name, issue_number=None):
    auth = Auth.Token(token)
    gh = Github(auth=auth)
    me = get_me(gh)
    repo = gh.get_repo(repo_name)
    
    # 重新初始化 README
    with open("README.md", "w", encoding="utf-8") as md:
        md.write(MD_HEAD)
    
    # 按顺序执行渲染
    add_md_recent(repo, "README.md", me)
    add_md_label(repo, "README.md", me)
    
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
