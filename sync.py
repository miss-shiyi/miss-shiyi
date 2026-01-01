# -*- coding: utf-8 -*-
import os, requests, re

TOKEN = os.environ.get('G_T')
REPO = "miss-shiyi/miss-shiyi"

def sync():
    if not os.path.exists("_posts"):
        os.makedirs("_posts")
    
    # 彻底清理旧文章，防止重名导致报错
    for file in os.listdir("_posts"):
        os.remove(os.path.join("_posts", file))

    url = f"https://api.github.com/repos/{REPO}/issues?state=open"
    headers = {"Authorization": f"token {TOKEN}"}
    
    try:
        issues = requests.get(url, headers=headers).json()
        for issue in issues:
            if "pull_request" in issue: continue
            
            date = issue['created_at'].split('T')[0]
            # 过滤特殊字符，防止 Jekyll 构建失败
            clean_title = re.sub(r'[^\w\s-]', '', issue['title']).strip().replace(" ", "-")
            filename = f"_posts/{date}-{issue['number']}-{clean_title}.md"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write("---\n")
                f.write("layout: post\n") # 核心：必须有这行才有样式
                f.write(f"title: \"{issue['title']}\"\n")
                f.write(f"date: {issue['created_at']}\n")
                # 标签同步
                tags = [l['name'] for l in issue['labels']]
                if tags: f.write(f"tags: {tags}\n")
                f.write("---\n\n")
                # 写入正文
                f.write(issue['body'] if issue['body'] else "")
        print("✅ 同步成功")
    except Exception as e:
        print(f"❌ 出错了: {e}")

if __name__ == "__main__":
    sync()
