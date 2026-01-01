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

    url = f"https://api.github.com/repos/{REPO}/issues?state=open"
    headers = {"Authorization": f"token {TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        issues = response.json()
        if not isinstance(issues, list): return
        
        readme_list = []

        for issue in issues:
            if "pull_request" in issue: continue
            
            # 基础信息
            labels = [l['name'] for l in issue['labels']]
            cat = labels[0] if labels else "未分类"
            date = issue['created_at'].split('T')[0]
            clean_title = re.sub(r'[^\w\s-]', '', issue['title']).strip().replace(" ", "-")
            
            # --- 1. 写入主仓库 BACKUP (带分类文件夹) ---
            cat_dir = os.path.join(backup_dir, cat)
            if not os.path.exists(cat_dir): os.makedirs(cat_dir)
            main_file_name = f"{date}-{clean_title}.md"
            with open(os.path.join(cat_dir, main_file_name), "w", encoding="utf-8") as f:
                f.write(f"# {issue['title']}\n\n{issue['body'] or ''}")

            # --- 2. 写入 Wiki 临时目录 (扁平化命名) ---
            wiki_file_name = f"[{cat}] {date}-{clean_title}.md"
            with open(os.path.join(wiki_temp, wiki_file_name), "w", encoding="utf-8") as f:
                f.write(f"# {issue['title']}\n\n> **分类**: {cat} | **日期**: {date}\n\n---\n\n{issue['body'] or ''}")

            # --- 3. 准备 README 列表 ---
            rel_path = f"BACKUP/{cat}/{main_file_name}".replace(" ", "%20")
            readme_list.append(f"- [{issue['title']}]({rel_path}) — `{date}` ({cat})")

        # 更新 README
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# 拾遗集\n\n> [📖 点击进入 Wiki 沉浸阅读](https://github.com/{REPO}/wiki)\n\n### 📝 最近备份\n\n" + "\n".join(readme_list))

        print("✅ 脚本执行完成")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    sync()
