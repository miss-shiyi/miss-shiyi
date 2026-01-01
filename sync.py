# -*- coding: utf-8 -*-
import os, requests, re
from collections import defaultdict

TOKEN = os.environ.get('G_T')
REPO = "miss-shiyi/miss-shiyi"

def sync():
    url = f"https://api.github.com/repos/{REPO}/issues?state=open"
    headers = {"Authorization": f"token {TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        issues = response.json()
        
        # 按分类存储：{ "分类名": ["文章链接1", "文章链接2"] }
        categories = defaultdict(list)

        for issue in issues:
            if "pull_request" in issue: continue
            
            # 获取分类（Label），如果没有标签则归类为 "未分类"
            labels = [l['name'] for l in issue['labels']]
            category_name = labels[0] if labels else "未分类"
            
            date = issue['created_at'].split('T')[0]
            # 链接直接指向 Issue 页面，点击即看，最稳定
            link = f"- [{issue['title']}]({issue['html_url']}) — `{date}`"
            categories[category_name].append(link)

        # 构建 README 内容
        with open("README.md", "w", encoding="utf-8") as f:
            f.write("# 拾遗集\n\n")
            f.write("> 不属于任何人，也不拥有任何人。\n\n")
            
            # 遍历分类写入
            for cat, posts in categories.items():
                f.write(f"### 📁 {cat}\n")
                f.write("\n".join(posts))
                f.write("\n\n")
            
            f.write("---\n")
            f.write(f"*上次同步时间: {issues[0]['updated_at'] if issues else 'N/A'} (UTC)*")

        print("✅ README 列表已按分类同步完成")
    except Exception as e:
        print(f"❌ 运行出错: {e}")

if __name__ == "__main__":
    sync()
