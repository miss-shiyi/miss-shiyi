# -*- coding: utf-8 -*-
import os, requests, re, shutil
from collections import defaultdict

TOKEN = os.environ.get('G_T')
REPO = "miss-shiyi/miss-shiyi"

def sync():
    # 1. 核心逻辑：先彻底删除旧备份目录，确保“同步删除”
    backup_dir = "BACKUP"
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    os.makedirs(backup_dir)

    # 只抓取 Open 状态的 Issue
    url = f"https://api.github.com/repos/{REPO}/issues?state=open"
    headers = {"Authorization": f"token {TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        issues = response.json()
        
        # 错误处理：如果 API 返回报错
        if not isinstance(issues, list):
            print(f"❌ API 错误: {issues}")
            return

        categories = defaultdict(list)

        for issue in issues:
            if "pull_request" in issue: continue
            
            # 获取分类（Label）
            labels = [l['name'] for l in issue['labels']]
            cat = labels[0] if labels else "未分类"
            
            # 处理文件名（日期-标题.md）
            date = issue['created_at'].split('T')[0]
            clean_title = re.sub(r'[^\w\s-]', '', issue['title']).strip().replace(" ", "-")
            
            # --- 建立物理备份 ---
            cat_dir = os.path.join(backup_dir, cat)
            if not os.path.exists(cat_dir):
                os.makedirs(cat_dir)
            
            file_name = f"{date}-{clean_title}.md"
            file_path = os.path.join(cat_dir, file_name)
            
            with open(file_path, "w", encoding="utf-8") as f:
                # 写入 Frontmatter 方便后续可能的迁移
                f.write("---\n")
                f.write(f"title: \"{issue['title']}\"\n")
                f.write(f"date: {issue['created_at']}\n")
                f.write(f"category: {cat}\n")
                f.write("---\n\n")
                f.write(issue['body'] if issue['body'] else "")

            # --- 准备 README 列表链接 ---
            # 链接直接指向仓库内的备份文件
            relative_url = f"BACKUP/{cat}/{file_name}".replace(" ", "%20")
            item = f"- [{issue['title']}]({relative_url}) — `{date}`"
            categories[cat].append(item)

        # 2. 写入 README.md
        with open("README.md", "w", encoding="utf-8") as f:
            f.write("# 拾遗集\n\n")
            f.write("> 不属于任何人，也不拥有任何人。\n\n")
            
            # 按分类字母顺序展示
            for cat in sorted(categories.keys()):
                f.write(f"### 📁 {cat}\n")
                # 分类下按日期降序
                f.write("\n".join(categories[cat]))
                f.write("\n\n")
            
            f.write("---\n")
            f.write(f"*最后同步: {issues[0]['updated_at'] if issues else 'N/A'}*")

        print("✅ 备份与 README 已完全同步。")
    except Exception as e:
        print(f"❌ 运行失败: {e}")

if __name__ == "__main__":
    sync()
