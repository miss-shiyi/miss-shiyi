# -*- coding: utf-8 -*-
import argparse, os, re, shutil
from github import Github, Auth

def setup_directories():
    # 每次运行先清理旧文章，确保 Issue 删除后本地同步删除
    path = os.path.join("content", "posts")
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

def clean_title(title):
    # 彻底移除可能导致构建问题的特殊字符
    return re.sub(r'[\\/:*?"<>|]', '', title).strip().replace(" ", "-")

def main(token, repo_name):
    gh = Github(auth=Auth.Token(token))
    repo = gh.get_repo(repo_name)
    setup_directories()
    
    issues = repo.get_issues(state="open")
    
    for issue in issues:
        if issue.pull_request: continue
            
        safe_title = clean_title(issue.title)
        filepath = os.path.join("content", "posts", f"{issue.number}_{safe_title}.md")

        with open(filepath, "w", encoding="utf-8") as f:
            # Hugo 必须的元数据：YAML 格式
            f.write("---\n")
            f.write(f"title: \"{issue.title}\"\n")
            # 格式必须符合 ISO 8601，否则 Hugo 报错
            f.write(f"date: {issue.created_at.strftime('%Y-%m-%dT%H:%M:%S+08:00')}\n")
            f.write(f"lastmod: {issue.updated_at.strftime('%Y-%m-%dT%H:%M:%S+08:00')}\n")
            
            labels = [l.name for l in issue.labels]
            if labels:
                f.write(f"categories: {labels}\n")
                f.write(f"tags: {labels}\n")
            
            f.write("---\n\n")
            
            # Hugo 直接渲染原始文本，Swift 的 <T> 会被正确处理，不丢高亮
            f.write(issue.body if issue.body else "")

    print("✅ Hugo 文章同步完成")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token"); parser.add_argument("repo_name")
    args = parser.parse_args()
    main(args.github_token, args.repo_name)
