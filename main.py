# -*- coding: utf-8 -*-
import argparse
import os
import re
from datetime import timezone
from github import Github, Auth, GithubException
from marko.ext.gfm import gfm as marko
from feedgen.feed import FeedGenerator
from lxml.etree import CDATA

# --- 配置区 ---
MD_HEAD = """# 🌙 miss-shiyi's Digital Garden
> **"不属于任何人，也不拥有任何人，减少期待，好好生活，此程山高路远，我留给自己。"**
---
"""

BACKUP_DIR = "BACKUP"
ANCHOR_NUMBER = 5
# 确保这些标签名与你 GitHub 上的完全一致（包括大小写）
IGNORE_LABELS = ["Friends", "Top", "TODO"]
LABEL_ICONS = {"Python": "🐍", "Life": "🌱", "Automation": "🤖", "Code": "💻"}

def get_me(gh):
    me = os.getenv("GITHUB_NAME")
    return me if me else gh.get_user().login

def format_time(time):
    return time.strftime("%b %d, %Y")

def add_issue_info(issue, md):
    time_str = format_time(issue.created_at)
    md.write(f"- `[{time_str}]` &nbsp; **[{issue.title}]({issue.html_url})** \n")

def add_md_label(repo, md_path, me):
    labels = repo.get_labels()
    # 侧边栏初始化：首页必须放在最上面
    sidebar_content = ["* [🏠 首页](README.md)\n\n"]
    
    all_issues = list(repo.get_issues(state="open"))

    with open(md_path, "a+", encoding="utf-8") as md:
        md.write("## 📂 文章分类 (Categories)\n\n") # 显式写入标题
        
        for label in labels:
            # 过滤掉 GitHub 默认的无关标签，但保留你的自定义分类
            if label.name in ["bug", "help wanted", "invalid", "question"]: continue
            if label.name in IGNORE_LABELS: continue

            # 匹配文章
            issues_in_label = [i for i in all_issues if label.name in [l.name for l in i.labels]]
            if not issues_in_label: continue

            icon = LABEL_ICONS.get(label.name, "🔖")
            # 写入 README
            md.write(f"### {icon} {label.name}\n")
            # 写入 侧边栏结构
            sidebar_content.append(f"* **{icon} {label.name}**\n")
            
            issues_in_label.sort(key=lambda x: x.created_at, reverse=True)

            for issue in issues_in_label:
                # 写入 README 列表
                time_str = issue.created_at.strftime("%Y-%m-%d")
                md.write(f"- `[{time_str}]` [{issue.title}]({issue.html_url})\n")
                
                # 写入 侧边栏子项 (关键：Docsify 识别的路径)
                safe_title = re.sub(r'[\\/:*?"<>|]', '_', issue.title)
                sidebar_content.append(f"  * [{issue.title}](BACKUP/{issue.number}_{safe_title}.md)\n")
            md.write("\n")

    # 强制覆盖生成 _sidebar.md
    with open("_sidebar.md", "w", encoding="utf-8") as sb:
        sb.writelines(sidebar_content)
        
def generate_rss_feed(repo, filename, me):
    fg = FeedGenerator()
    fg.id(repo.html_url)
    fg.title(f"{me}'s Blog")
    fg.link(href=repo.html_url, rel='alternate')
    for issue in repo.get_issues(state="open"):
        if not issue.body or issue.user.login != me or issue.pull_request: continue
        fe = fg.add_entry()
        fe.id(issue.html_url)
        fe.title(issue.title)
        fe.published(issue.created_at.replace(tzinfo=timezone.utc))
        content = "".join(c for c in issue.body if ord(c) >= 32)
        fe.content(CDATA(marko.convert(content)), type="html")
    fg.atom_file(filename)

def main(token, repo_name, issue_number=None):
    auth = Auth.Token(token)
    gh = Github(auth=auth)
    me = get_me(gh)
    repo = gh.get_repo(repo_name)
    
    # 强制重新生成 README.md，清空旧内容
    with open("README.md", "w", encoding="utf-8") as md:
        md.write(MD_HEAD)
    
    # 运行核心逻辑
    add_md_label(repo, "README.md", me)
    generate_rss_feed(repo, "feed.xml", me)
    
    if not os.path.exists(BACKUP_DIR): os.mkdir(BACKUP_DIR)
    for issue in repo.get_issues(state="open"):
        if issue.user.login == me and not issue.pull_request:
            safe_title = re.sub(r'[\\/:*?"<>|]', '_', issue.title)
            with open(os.path.join(BACKUP_DIR, f"{issue.number}_{safe_title}.md"), "w", encoding="utf-8") as f:
                f.write(f"# [{issue.title}]({issue.html_url})\n\n{issue.body}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token")
    parser.add_argument("repo_name")
    parser.add_argument("--issue_number", default=None)
    args = parser.parse_args()
    main(args.github_token, args.repo_name, args.issue_number)
