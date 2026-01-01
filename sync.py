# -*- coding: utf-8 -*-
import os, requests, re

# 从环境变量中读取，名称必须与 yml 中的一致
# 这里的 'G_T' 对应 yml 里的 G_T: ${{ secrets.G_T }}
TOKEN = os.environ.get('G_T')
REPO = "miss-shiyi/miss-shiyi"

def sync_issues():
    # 确保 _posts 文件夹存在
    if not os.path.exists("_posts"):
        os.makedirs("_posts")
    
    # 这里的 API 请求带上 Token，防止被 GitHub 频率限制
    url = f"https://api.github.com/repos/{REPO}/issues?state=open"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ 抓取失败: {response.status_code}")
        return
        
    issues = response.json()

    for issue in issues:
        if "pull_request" in issue: continue
        
        # 1. 提取日期
        date = issue['created_at'].split('T')[0]
        # 2. 清理文件名，确保 Jekyll 能识别
        safe_title = re.sub(r'[\\/:*?"<>|]', '', issue['title']).strip().replace(" ", "-")
        filename = f"_posts/{date}-{issue['number']}-{safe_title}.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write("layout: post\n")
            f.write(f"title: \"{issue['title']}\"\n")
            f.write(f"date: {issue['created_at']}\n")
            # 自动转换 Label 为 Tags
            labels = [l['name'] for l in issue['labels']]
            if labels:
                f.write(f"tags: {labels}\n")
            f.write("---\n\n")
            f.write(issue['body'] if issue['body'] else "")
            
    print(f"✅ 成功同步 {len(issues)} 篇笔记到 _posts 目录")

if __name__ == "__main__":
    sync_issues()
