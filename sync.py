# -*- coding: utf-8 -*-
import os, requests, re, shutil
from collections import defaultdict

TOKEN = os.environ.get('G_T')
REPO = "miss-shiyi/miss-shiyi"

def sync():
    # 准备目录
    backup_dir = "BACKUP"
    wiki_temp = "wiki_temp"
    for d in [backup_dir, wiki_temp]:
        if os.path.exists(d): shutil.rmtree(d)
        os.makedirs(d)

    headers = {"Authorization": f"token {TOKEN}"}
    all_issues = []
    page = 1

    # --- 核心修复：循环请求所有分页 ---
    while True:
        url = f"https://api.github.com/repos/{REPO}/issues?state=open&per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        issues = response.json()
        
        if not issues or not isinstance(issues, list): # 如果没有更多数据了，跳出循环
            break
        
        all_issues.extend(issues)
        page += 1

    readme_list = []
    categories = defaultdict(list)

    for issue in all_issues:
        if "pull_request" in issue: continue
        
        labels = [l['name'] for l in issue['labels']]
        cat = labels[0] if labels else "未分类"
        date = issue['created_at'].split('T')[0]
        # 移除了特殊字符，防止 Wiki 渲染和文件名报错
        clean_title = re.sub(r'[^\w\s-]', '', issue['title']).strip().replace(" ", "-")
        
        # 1. 物理备份
        cat_dir = os.path.join(backup_dir, cat)
        if not os.path.exists(cat_dir): os.makedirs(cat_dir)
        main_file_name = f"{date}-{clean_title}.md"
        with open(os.path.join(cat_dir, main_file_name), "w", encoding="utf-8") as f:
            f.write(f"# {issue['title']}\n\n{issue['body'] or ''}")

        # 2. Wiki 备份
        wiki_file_name = f"[{cat}] {date}-{clean_title}.md"
        with open(os.path.join(wiki_temp, wiki_file_name), "w", encoding="utf-8") as f:
            f.write(f"# {issue['title']}\n\n> **分类**: {cat} | **日期**: {date}\n\n---\n\n{issue['body'] or ''}")

        # 3. 记录到列表（按分类分组）
        rel_path = f"BACKUP/{cat}/{main_file_name}".replace(" ", "%20")
        categories[cat].append(f"- [{issue['title']}]({rel_path}) — `{date}`")

    # 4. 构建 README：按分类展示，防止列表太长混乱
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(f"# 拾遗集\n\n> [📖 点击进入 Wiki 沉浸阅读](https://github.com/{REPO}/wiki)\n\n")
        for cat_name in sorted(categories.keys()):
            f.write(f"### 📁 {cat_name}\n")
            f.write("\n".join(categories[cat_name]))
            f.write("\n\n")
        f.write("---\n")
        f.write(f"*最后全量同步时间: {all_issues[0]['updated_at'] if all_issues else 'N/A'}*")

    print(f"✅ 全量同步完成，共计 {len(all_issues)} 个 Issue。")

if __name__ == "__main__":
    sync()
