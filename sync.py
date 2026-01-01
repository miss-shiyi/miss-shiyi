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

    # 1. 全量获取所有 Issue (确保 218+ 条完整)
    while True:
        url = f"https://api.github.com/repos/{REPO}/issues?state=open&per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        issues = response.json()
        if not issues or not isinstance(issues, list): break
        all_issues.extend(issues)
        if len(issues) < 100: break
        page += 1

    # 按分类（Label）组织数据
    categories = defaultdict(list)

    for issue in all_issues:
        if "pull_request" in issue: continue
        
        labels = [l['name'] for l in issue['labels']]
        cat = labels[0] if labels else "未分类"
        date = issue['created_at'].split('T')[0]
        
        # 清理文件名非法字符
        clean_title = re.sub(r'[\/\\:\*\?"<>\|]', '', issue['title']).strip().replace(" ", "-")
        
        # --- A. 写入主仓库 BACKUP (物理备份) ---
        cat_dir = os.path.join(backup_dir, cat)
        if not os.path.exists(cat_dir): os.makedirs(cat_dir)
        main_file_name = f"{date}-{clean_title}.md"
        with open(os.path.join(cat_dir, main_file_name), "w", encoding="utf-8") as f:
            f.write(f"# {issue['title']}\n\n{issue['body'] or ''}")

        # --- B. 写入 Wiki 临时目录 ---
        wiki_file_name = f"[{cat}] {date}-{clean_title}.md"
        with open(os.path.join(wiki_temp, wiki_file_name), "w", encoding="utf-8") as f:
            f.write(f"# {issue['title']}\n\n> 分类: {cat} | 日期: {date}\n\n---\n\n{issue['body'] or ''}")

        # --- C. 记录列表数据 ---
        rel_path = f"BACKUP/{cat}/{main_file_name}".replace(" ", "%20")
        categories[cat].append(f"- [{issue['title']}]({rel_path}) — `{date}`")

    # --- D. 优化生成 README (实现折叠效果) ---
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(f"# 拾遗集\n\n")
        f.write(f"> [📖 进入 Wiki 沉浸阅读](https://github.com/{REPO}/wiki)\n\n")
        f.write(f"共有 {len(all_issues)} 篇笔记，已按分类归档：\n\n---\n\n")

        for cat_name in sorted(categories.keys()):
            posts = categories[cat_name]
            f.write(f"### 📁 {cat_name} ({len(posts)})\n")
            
            # 展示前 5 条
            visible_posts = posts[:5]
            f.write("\n".join(visible_posts) + "\n")
            
            # 超过 5 条的部分进行折叠
            if len(posts) > 5:
                hidden_posts = posts[5:]
                f.write("\n<details>\n")
                f.write(f"<summary>点击展开更多 ({len(hidden_posts)} 篇)</summary>\n\n")
                f.write("\n".join(hidden_posts) + "\n")
                f.write("\n</details>\n")
            
            f.write("\n")

        f.write("---\n")
        f.write(f"*上次更新: {all_issues[0]['updated_at'] if all_issues else 'N/A'}*")

    print(f"✅ README 已优化，处理文章: {len(all_issues)} 篇")

if __name__ == "__main__":
    sync()
