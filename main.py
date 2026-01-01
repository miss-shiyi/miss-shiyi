# -*- coding: utf-8 -*-
import argparse, os, re, shutil
from github import Github, Auth

def setup_directories():
    # 彻底清理所有旧目录，防止旧缓存干扰
    for d in ["content", "data", "public"]:
        if os.path.exists(d):
            shutil.rmtree(d)
    os.makedirs(os.path.join("content", "posts"))
    os.makedirs(os.path.join("content", "archives"))
    os.makedirs("data")

def main(token, repo_name):
    gh = Github(auth=Auth.Token(token))
    repo = gh.get_repo(repo_name)
    setup_directories()
    
    # --- 绝杀：直接在 data 目录生成侧边栏数据，绕过 hugo.yaml 的解析 Bug ---
    # 这会强制定义 sidebar 及其内部的 enabled 字段
    with open("data/sidebar.json", "w", encoding="utf-8") as f:
        f.write('{"enabled": true}')

    # 生成归档页
    with open("content/archives/index.md", "w", encoding="utf-8") as f:
        f.write("---\ntitle: \"归档\"\nlayout: \"archives\"\n---\n")

    # 同步 Issues
    issues = repo.get_issues(state="open")
    for issue in issues:
        if issue.pull_request: continue
        safe_title = re.sub(r'[\\/:*?"<>|]', '', issue.title).strip().replace(" ", "-")
        post_dir = os.path.join("content", "posts", f"{issue.number}_{safe_title}")
        os.makedirs(post_dir, exist_ok=True)
        
        with open(os.path.join(post_dir, "index.md"), "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write(f"title: \"{issue.title}\"\n")
            f.write(f"date: {issue.created_at.strftime('%Y-%m-%dT%H:%M:%S+08:00')}\n")
            f.write(f"image: \"https://picsum.photos/seed/{issue.number}/800/400\"\n")
            # 强制在每篇文章的元数据里也注入 sidebar 状态（三重保险）
            f.write("sidebar: \n  enabled: true\n")
            labels = [l.name for l in issue.labels]
            if labels: f.write(f"categories: {labels}\n")
            f.write("---\n\n")
            f.write(issue.body if issue.body else "")

    print("✅ 数据注入完成，准备构建")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token"); parser.add_argument("repo_name")
    args = parser.parse_args()
    main(args.github_token, args.repo_name)
