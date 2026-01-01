# -*- coding: utf-8 -*-
import os, requests, re, shutil
from collections import defaultdict

TOKEN = os.environ.get('G_T')
REPO = "miss-shiyi/miss-shiyi"

def sync():
    # 准备清理目录
    backup_dir = "BACKUP"
    wiki_temp = "wiki_temp"
    for d in [backup_dir, wiki_temp]:
        if os.path.exists(d): shutil.rmtree(d)
        os.makedirs(d)

    headers = {"Authorization": f"token {TOKEN}"}
    all_issues = []
    page = 1

    # --- 确保 218 条全部抓取的循环 ---
    while True:
        url = f"https://api.github.com/repos/{REPO}/issues?state=open&per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        issues = response.json()
        
        # 如果没有数据或返回不是列表，停止抓取
        if not issues or not isinstance(issues, list):
            break
        
        all_issues.extend(issues)
        # 如果这一页不足100条，说明已经是最后一页了
        if len(issues) < 100:
            break
        page += 1

    categories = defaultdict(list)

    for issue in all_issues:
        if "pull_request" in issue: continue
        
        # 获取标签
        labels = [l['name'] for l in issue['labels']]
        cat = labels[0] if labels else "未分类"
        date = issue['created_at'].split('T')[0]
        
        # 文件名清洗：保留中文，只剔除系统非法字符
        clean_title = re.sub(r'[\/\\:\*\?"<>\|]', '', issue['title']).strip().replace(" ", "-")
        
        # 1. 物理备份 (主仓库)
        cat_dir = os.path.join(backup_dir, cat)
        if not os.path.exists(cat_dir): os.makedirs(cat_dir)
        main_file_name = f"{date}-{clean_title}.md"
        with open(os.path.join(cat_dir, main_file_name), "w", encoding="utf-8") as f:
            f.write(f"# {issue['title']}\n\n{issue['body'] or ''}")

        # 2. Wiki 备份 (扁平化)
        wiki_file_name = f"[{cat}] {date}-{clean_title}.md"
        with open(os.path.join(wiki_temp, wiki_file_name), "w", encoding="utf-8") as f:
            f.write(f"# {issue['title']}\n\n> **分类**: {cat} | **日期**: {date}\n\n---\n\n{issue['body'] or ''}")

        # 3. README 列表数据
        rel_path = f"BACKUP/{cat}/{main_file_name}".replace(" ", "%20")
        categories[cat].append(f"- [{issue['title']}]({rel_path}) — `{date}`")

    # 4. 写入 README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(f"# 拾遗集\n\n> [📖 点击进入 Wiki 沉浸阅读](https://github.com/{REPO}/wiki)\n\n")
        # 按照分类名称排序显示
        for cat_name in sorted(categories.keys()):
            f.write(f"### 📁 {cat_name}\n")
            f.write("\n".join(categories[cat_name]))
            f.write("\n\n")
        f.write("---\n")
        f.write(f"*当前共计文章: {len(all_issues)} 篇*")

    print(f"✅ 同步完成，共处理 {len(all_issues)} 篇文章")

if __name__ == "__main__":
    sync()
