# -*- coding: utf-8 -*-
import os, requests, re, shutil
from collections import defaultdict

TOKEN = os.environ.get('G_T')
REPO = "miss-shiyi/miss-shiyi"

def sync():
    backup_dir = "BACKUP"
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    os.makedirs(backup_dir)

    url = f"https://api.github.com/repos/{REPO}/issues?state=open"
    headers = {"Authorization": f"token {TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        issues = response.json()
        categories = defaultdict(list)

        for issue in issues:
            if "pull_request" in issue: continue
            
            labels = [l['name'] for l in issue['labels']]
            cat = labels[0] if labels else "未分类"
            
            date = issue['created_at'].split('T')[0]
            clean_title = re.sub(r'[^\w\s-]', '', issue['title']).strip().replace(" ", "-")
            
            # --- 1. 生成物理文件 ---
            cat_dir = os.path.join(backup_dir, cat)
            if not os.path.exists(cat_dir):
                os.makedirs(cat_dir)
            
            file_name = f"{date}-{clean_title}.md"
            file_path = os.path.join(cat_dir, file_name)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {issue['title']}\n\n") # 在文件开头加个大标题
                f.write(issue['body'] if issue['body'] else "")

            # --- 2. 关键修改：指向仓库内的 MD 文件 ---
            # 使用相对路径，GitHub README 会自动将其解析为仓库文件链接
            # 空格需要转换为 %20 确保链接有效
            relative_path = f"BACKUP/{cat}/{file_name}".replace(" ", "%20")
            
            # 这样点击后会进入：github.com/用户名/仓库名/blob/main/BACKUP/分类/文件名.md
            item = f"- [{issue['title']}]({relative_path}) — `{date}`"
            categories[cat].append(item)

        # 写入 README.md
        with open("README.md", "w", encoding="utf-8") as f:
            f.write("# 拾遗集\n\n")
            f.write("> 不属于任何人，也不拥有任何人。\n\n")
            for cat in sorted(categories.keys()):
                f.write(f"### 📁 {cat}\n")
                f.write("\n".join(categories[cat]))
                f.write("\n\n")
            f.write("---\n")
            f.write(f"*上次同步: {issues[0]['updated_at'] if issues else 'N/A'}*")

        print("✅ 已更新 README 链接至本地备份文件")
    except Exception as e:
        print(f"❌ 运行失败: {e}")

if __name__ == "__main__":
    sync()
