# -*- coding: utf-8 -*-
import argparse
import os
import re
from datetime import timezone
from github import Github, Auth
from marko.ext.gfm import gfm as marko
from feedgen.feed import FeedGenerator
from lxml.etree import CDATA

# --- 配置 ---
MD_HEAD = """# 🌙 miss-shiyi's Digital Garden
> **"不属于任何人，也不拥有任何人，减少期待，好好生活。"**
---
"""

BACKUP_DIR = "BACKUP"
ANCHOR_NUMBER = 5
IGNORE_LABELS = ["Friends", "Top", "TODO", "bug", "help wanted", "invalid", "question"]
LABEL_ICONS = {"Python": "🐍", "Life": "🌱", "Automation": "🤖", "Code": "💻"}

def format_time(time):
    return time.strftime("%Y-%m-%d")

def add_md_recent(repo, md_path, limit=5):
    print("开始生成：最近更新...")
    with open(md_path, "a+", encoding="utf-8") as md:
        md.write("## 🕒 最近更新\n")
        issues = repo.get_issues(state="open", sort="updated")
        count = 0
        for issue in issues:
            if issue.pull_request: continue
            time_str = format_time(issue.created_at)
            md.write(f"- `[{time_str}]` [{issue.title}]({issue.html_url})\n")
            count += 1
            if count >= limit: break
        md.write("\n---\n")

def add_md_label(repo, md_path):
    print("开始生成：文章分类...")
    labels = list(repo.get_labels())
    print(f"仓库内总共发现标签数: {len(labels)}")
    
    sidebar_content = ["* [🏠 首页](README.md)\n\n"]
    
    with open(md_path, "a+", encoding="utf-8") as md:
        md.write("## 📂 文章分类\n\n")
        
        for label in labels:
            if label.name in IGNORE_LABELS:
                continue

            # 使用最稳妥的过滤方式
            issues = list(repo.get_issues(labels=[label], state="open"))
            if not issues:
                continue

            print(f"确认标签 [{label.name}] 下有 {len(issues)} 篇文章")
            
            icon = LABEL_ICONS.get(label.name, "🔖")
            md.write(f"### {icon} {label.name}\n")
            sidebar_content.append(f"* **{icon} {label.name}**\n")
            
            # 按时间倒序
            issues.sort(key=lambda x: x.created_at, reverse=True)
            
            for i, issue in enumerate(issues):
                if issue.pull_request: continue
                
                if i == ANCHOR_NUMBER:
                    md.write("<details><summary>显示更多</summary>\n\n")
                
                time_str = format_time(issue.created_at)
                md.write(f"- `[{time_str}]` [{issue.title}]({issue.html_url})\n")
                
                # 侧边栏路径同步
                safe_title = issue.title.replace(" ", ".")
                sidebar_content.append(f"  * [{issue.title}](BACKUP/{issue.number}_{safe_title}.md)\n")
            
            if len(issues) > ANCHOR_NUMBER:
                md.write("\n</details>\n")
            md.write("\n")

    with open("_sidebar.md", "w", encoding="utf-8") as sb:
        sb.writelines(sidebar_content)
    print("分类与侧边栏生成任务结束。")

def main(token, repo_name):
    auth = Auth.Token(token)
    gh = Github(auth=auth)
    repo = gh.get_repo(repo_name)
    
    # 1. 重置 README
    with open("README.md", "w", encoding="utf-8") as md:
        md.write(MD_HEAD)
    
    # 2. 生成最近更新
    add_md_recent(repo, "README.md")
    
    # 3. 生成分类 (关键步骤)
    add_md_label(repo, "README.md")
    
    # 4. 备份文件
    if not os.path.exists(BACKUP_DIR):
        os.mkdir(BACKUP_DIR)
    for issue in repo.get_issues(state="open"):
        if not issue.pull_request:
            safe_title = issue.title.replace(" ", ".")
            with open(os.path.join(BACKUP_DIR, f"{issue.number}_{safe_title}.md"), "w", encoding="utf-8") as f:
                f.write(f"# [{issue.title}]({issue.html_url})\n\n{issue.body}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token")
    parser.add_argument("repo_name")
    parser.add_argument("--issue_number", default=None)
    args = parser.parse_args()
    main(args.github_token, args.repo_name)
