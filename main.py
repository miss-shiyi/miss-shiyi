# -*- coding: utf-8 -*-
import argparse
import os
import json
from github import Github, Auth
from datetime import timezone

# --- 配置 ---
# 首页 README 内容（对应归档页）
MD_HEAD = """# 📚 全部分类与存档
> **"不属于任何人，也不拥有任何人，减少期待，好好生活。"**
---
"""

BACKUP_DIR = "BACKUP"
IGNORE_LABELS = ["Friends", "Top", "TODO", "bug", "help wanted", "invalid", "question"]
LABEL_ICONS = {"Python": "🐍", "Life": "🌱", "Automation": "🤖", "Code": "💻"}

def format_time(time):
    return time.strftime("%Y-%m-%d")

def setup_directories():
    """确保目录存在"""
    for path in [BACKUP_DIR, ".vitepress"]:
        if not os.path.exists(path):
            os.makedirs(path)

def clean_title(title):
    """安全标题转换，VitePress 建议 URL 中不使用特殊字符"""
    # 移除或替换 Windows/Linux 文件系统敏感字符
    s = re.sub(r'[\\/:*?"<>|]', '', title)
    return s.replace(" ", "-")

import re

def main(token, repo_name):
    # --- 1. 初始化 Auth 与 Repo ---
    auth = Auth.Token(token)
    gh = Github(auth=auth)
    repo = gh.get_repo(repo_name)
    
    setup_directories()
    
    # 存储所有分类数据
    dict_by_labels = {}
    all_posts = []

    # --- 2. 获取并处理 Issues ---
    print("正在从 GitHub 获取 Issues...")
    issues = repo.get_issues(state="open")
    
    for issue in issues:
        if issue.pull_request:
            continue
            
        # 安全的文件名逻辑 (issue_number + title)
        safe_title = clean_title(issue.title)
        filename = f"{issue.number}_{safe_title}.md"
        filepath = os.path.join(BACKUP_DIR, filename)

        # 备份 Issue 内容到本地 Markdown
        with open(filepath, "w", encoding="utf-8") as f:
            # 增加一些 Frontmatter 给 VitePress（可选，用于显示更新日期）
            f.write(f"---\neditLink: false\nlastUpdated: {format_time(issue.updated_at)}\n---\n\n")
            f.write(f"# {issue.title}\n\n{issue.body if issue.body else ''}")

        # 整理分类信息
        labels = [l.name for l in issue.labels if l.name not in IGNORE_LABELS]
        if not labels:
            labels = ["未分类"]

        post_info = {
            "title": issue.title,
            # VitePress 链接不写 .md，且必须以 / 开头（相对于根目录）
            "link": f"/{BACKUP_DIR}/{issue.number}_{safe_title}",
            "created_at": format_time(issue.created_at)
        }
        
        for label in labels:
            if label not in dict_by_labels:
                dict_by_labels[label] = []
            dict_by_labels[label].append(post_info)
        
        all_posts.append(post_info)

    # --- 3. 生成 VitePress 侧边栏 (sidebar.json) ---
    print("生成 VitePress 侧边栏...")
    vite_sidebar = []
    
    # 按标签排序
    for label_name in sorted(dict_by_labels.keys()):
        posts = dict_by_labels[label_name]
        # 文章按创建时间倒序
        posts.sort(key=lambda x: x['created_at'], reverse=True)
        
        icon = LABEL_ICONS.get(label_name, "🔖")
        vite_sidebar.append({
            "text": f"{icon} {label_name}",
            "collapsed": True,
            "items": [{"text": p["title"], "link": p["link"]} for p in posts]
        })

    with open(".vitepress/sidebar.json", "w", encoding="utf-8") as f:
        json.dump(vite_sidebar, f, ensure_ascii=False, indent=2)

    # --- 4. 更新主页/归档页 README.md ---
    print("生成 README.md 归档页...")
    all_posts.sort(key=lambda x: x['created_at'], reverse=True)
    with open("README.md", "w", encoding="utf-8") as md:
        md.write(MD_HEAD)
        md.write("\n## 🕒 最近更新\n\n")
        for p in all_posts[:10]: # 最近更新展示前10条
            md.write(f"- `[{p['created_at']}]` [{p['title']}]({p['link']})\n")
        md.write("\n---\n\n## 📂 全部分类\n")
        for group in vite_sidebar:
            md.write(f"### {group['text']}\n")
            for item in group['items']:
                md.write(f"- [{item['text']}]({item['link']})\n")

    print("✅ 任务全部完成！")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token")
    parser.add_argument("repo_name")
    args = parser.parse_args()
    main(args.github_token, args.repo_name)
