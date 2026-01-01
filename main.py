# -*- coding: utf-8 -*-
import argparse
import os
import json
import re
from github import Github, Auth
from datetime import timezone

# --- 配置 ---
MD_HEAD = """# 📚 全部分类与存档
> **"不属于任何人，也不拥有任何人，减少期待，好好生活。"**
---
"""

BACKUP_DIR = "BACKUP"
IGNORE_LABELS = ["Friends", "Top", "TODO", "bug", "help wanted", "invalid", "question"]
LABEL_ICONS = {"Python": "🐍", "Life": "🌱", "Automation": "🤖", "Code": "💻", "Swift": "🍎"}

def format_time(time):
    return time.strftime("%Y-%m-%d")

def setup_directories():
    """确保目录存在"""
    for path in [BACKUP_DIR, ".vitepress"]:
        if not os.path.exists(path):
            os.makedirs(path)

def clean_title(title):
    """安全标题转换：移除特殊字符并处理空格"""
    # 移除 VitePress 路由中可能引起问题的特殊字符
    s = re.sub(r'[\\/:*?"<>|]', '', title)
    return s.replace(" ", "-")

def main(token, repo_name):
    # --- 1. 初始化 Auth 与 Repo ---
    auth = Auth.Token(token)
    gh = Github(auth=auth)
    repo = gh.get_repo(repo_name)
    
    setup_directories()
    
    dict_by_labels = {}
    all_posts = []

    # --- 2. 获取并处理 Issues ---
    print("正在从 GitHub 获取 Issues...")
    issues = repo.get_issues(state="open")
    
    for issue in issues:
        if issue.pull_request:
            continue
            
        safe_title = clean_title(issue.title)
        filename = f"{issue.number}_{safe_title}.md"
        filepath = os.path.join(BACKUP_DIR, filename)

        # 备份 Issue 内容到本地 Markdown
        with open(filepath, "w", encoding="utf-8") as f:
            # --- 关键修复：Frontmatter ---
            # 1. editLink: false 移除编辑链接
            # 2. lastUpdated 显示更新时间
            # 3. template: doc 确保作为文档渲染
            f.write(f"---\n")
            f.write(f"editLink: false\n")
            f.write(f"lastUpdated: {format_time(issue.updated_at)}\n")
            # 绝杀招式：禁用该页面的 Vue 功能，彻底解决 <T> 报错
            f.write(f"features: []\n")
            f.write(f"---\n\n")
            
            f.write(f"# {issue.title}\n\n")
            
            # 使用 v-pre 指令包裹正文，防止 Vue 解析正文中的特殊符号
            f.write('<div v-pre>\n\n')
            f.write(issue.body if issue.body else "")
            f.write('\n\n</div>\n')

        # 整理分类信息
        labels = [l.name for l in issue.labels if l.name not in IGNORE_LABELS]
        if not labels:
            labels = ["未分类"]

        # VitePress 链接不包含 .md，且开头必须带 / 适配 base 路径
        post_info = {
            "title": issue.title,
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
    for label_name in sorted(dict_by_labels.keys()):
        posts = dict_by_labels[label_name]
        posts.sort(key=lambda x: x['created_at'], reverse=True)
        
        icon = LABEL_ICONS.get(label_name, "🔖")
        vite_sidebar.append({
            "text": f"{icon} {label_name}",
            "collapsed": True,
            "items": [{"text": p["title"], "link": p["link"]} for p in posts]
        })

    with open(".vitepress/sidebar.json", "w", encoding="utf-8") as f:
        json.dump(vite_sidebar, f, ensure_ascii=False, indent=2)

    # --- 4. 更新归档页 README.md ---
    print("生成 README.md 归档页...")
    all_posts.sort(key=lambda x: x['created_at'], reverse=True)
    with open("README.md", "w", encoding="utf-8") as md:
        md.write(MD_HEAD)
        md.write("\n## 🕒 最近更新\n\n")
        for p in all_posts[:10]:
            md.write(f"- `[{p['created_at']}]` [{p['title']}]({p['link']})\n")
        md.write("\n---\n\n## 📂 全部分类\n")
        for group in vite_sidebar:
            md.write(f"### {group['text']}\n")
            for item in group['items']:
                md.write(f"- [{item['text']}]({item['link']})\n")

    print("✅ 全量同步完成，准备构建 VitePress。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token")
    parser.add_argument("repo_name")
    args = parser.parse_args()
    main(args.github_token, args.repo_name)
