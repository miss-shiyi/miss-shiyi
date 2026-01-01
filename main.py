# -*- coding: utf-8 -*-
import argparse, os, re, shutil
from github import Github, Auth

def setup_directories():
    if os.path.exists("content"):
        shutil.rmtree(d)
    os.makedirs(os.path.join("content", "posts"))
    os.makedirs(os.path.join("content", "archives"))
    os.makedirs(os.path.join("content", "categories"))

def main(token, repo_name):
    gh = Github(auth=Auth.Token(token))
    repo = gh.get_repo(repo_name)
    setup_directories()
    
    # 1. 归档页
    with open("content/archives/index.md", "w", encoding="utf-8") as f:
        f.write("---\ntitle: \"归档\"\nlayout: \"archives\"\n---\n")

    # 2. 同步 Issues
    issues = repo.get_issues(state="open")
    categories_found = set()

    for issue in issues:
        if issue.pull_request: continue
        safe_title = re.sub(r'[\\/:*?"<>|]', '', issue.title).strip().replace(" ", "-")
        post_dir = os.path.join("content", "posts", f"{issue.number}_{safe_title}")
        os.makedirs(post_dir, exist_ok=True)
        
        labels = [l.name for l in issue.labels]
        for label in labels: categories_found.add(label)

        with open(os.path.join(post_dir, "index.md"), "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write(f"title: \"{issue.title}\"\n")
            f.write(f"date: {issue.created_at.strftime('%Y-%m-%dT%H:%M:%S+08:00')}\n")
            f.write(f"image: \"https://picsum.photos/seed/{issue.number}/800/400\"\n")
            # 这里的字段必须叫 categories
            if labels: f.write(f"categories: {labels}\n")
            f.write("---\n\n")
            f.write(issue.body if issue.body else "")

    # 3. 【关键】为每个分类生成 _index.md，否则 Stack 不显示分类
    for cat in categories_found:
        cat_dir = os.path.join("content", "categories", cat)
        os.makedirs(cat_dir, exist_ok=True)
        with open(os.path.join(cat_dir, "_index.md"), "w", encoding="utf-8") as f:
            f.write(f"---\ntitle: \"{cat}\"\n---\n")

    print(f"✅ 同步完成，共识别分类: {list(categories_found)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token"); parser.add_argument("repo_name")
    args = parser.parse_args()
    main(args.github_token, args.repo_name)
