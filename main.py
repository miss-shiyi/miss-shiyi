# -*- coding: utf-8 -*-
import argparse, os, re, shutil
from github import Github, Auth

def setup_directories():
    # 清理并重建 content 目录
    if os.path.exists("content"):
        shutil.rmtree("content")
    os.makedirs(os.path.join("content", "posts"))
    # 创建归档页
    os.makedirs(os.path.join("content", "archives"))

def clean_title(title):
    return re.sub(r'[\\/:*?"<>|]', '', title).strip().replace(" ", "-")

def main(token, repo_name):
    gh = Github(auth=Auth.Token(token))
    repo = gh.get_repo(repo_name)
    setup_directories()
    
    # 1. 生成归档页面配置
    with open(os.path.join("content", "archives", "index.md"), "w", encoding="utf-8") as f:
        f.write("---\ntitle: \"归档\"\nlayout: \"archives\"\n---\n")

    # 2. 同步 Issues
    issues = repo.get_issues(state="open")
    for issue in issues:
        if issue.pull_request: continue
        safe_title = clean_title(issue.title)
        post_dir = os.path.join("content", "posts", f"{issue.number}_{safe_title}")
        os.makedirs(post_dir, exist_ok=True)
        
        with open(os.path.join(post_dir, "index.md"), "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write(f"title: \"{issue.title}\"\n")
            f.write(f"date: {issue.created_at.strftime('%Y-%m-%dT%H:%M:%S+08:00')}\n")
            # 随机封面图兜底
            f.write(f"image: \"https://picsum.photos/seed/{issue.number}/800/400\"\n")
            labels = [l.name for l in issue.labels]
            if labels: f.write(f"categories: {labels}\n")
            f.write("---\n\n")
            f.write(issue.body if issue.body else "")

    print("✅ Stack 内容同步完成")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token"); parser.add_argument("repo_name")
    args = parser.parse_args()
    main(args.github_token, args.repo_name)
