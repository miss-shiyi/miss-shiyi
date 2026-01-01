# -*- coding: utf-8 -*-
import os, requests, re

TOKEN = os.environ.get('G_T')
REPO = "miss-shiyi/miss-shiyi"

def sync():
    if not os.path.exists("_posts"):
        os.makedirs("_posts")
    
    for file in os.listdir("_posts"):
        os.remove(os.path.join("_posts", file))

    url = f"https://api.github.com/repos/{REPO}/issues?state=open"
    headers = {"Authorization": f"token {TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        issues = response.json()
        readme_list = []

        for issue in issues:
            if "pull_request" in issue: continue
            
            date = issue['created_at'].split('T')[0]
            # 这里的标题清理是关键，防止 URL 乱码
            clean_title = re.sub(r'[^\w\s-]', '', issue['title']).strip().replace(" ", "-")
            filename = f"_posts/{date}-{issue['number']}-{clean_title}.md"
            
            # 修正 README 链接：Jekyll 默认路径是 /年/月/日/标题.html
            site_link = f"https://miss-shiyi.github.io/miss-shiyi/{date.replace('-','/')}/{clean_title}.html"
            readme_list.append(f"- [{issue['title']}]({site_link}) — `{date}`")

            with open(filename, "w", encoding="utf-8") as f:
                f.write("---\n")
                f.write("layout: post\n")
                f.write(f"title: \"{issue['title']}\"\n")
                f.write(f"date: {issue['created_at']}\n")
                # 写入标签，Minima 会自动分类
                labels = [l['name'] for l in issue['labels']]
                if labels: f.write(f"tags: {labels}\n")
                f.write("---\n\n")
                f.write(issue['body'] if issue['body'] else "")

        # 恢复被我弄丢的 README 列表
        with open("README.md", "w", encoding="utf-8") as f:
            f.write("# 拾遗集\n\n")
            f.write("> 不属于任何人，也不拥有任何人。\n\n")
            f.write("### 📝 笔记存档\n\n")
            f.write("\n".join(readme_list) if readme_list else "暂无文章")
            f.write(f"\n\n---\n*Last sync: {issues[0]['updated_at'] if issues else 'N/A'}*")

        print("✅ README 和文章已同步")
    except Exception as e:
        print(f"❌ 失败: {e}")

if __name__ == "__main__":
    sync()
