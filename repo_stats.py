#!/usr/bin/env python3
"""Repo stats CLI. Usage: python repo_stats.py owner/repo"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error

API = "https://api.github.com"


def _get(path, token=None):
    # // GitHub requires a UA header, and a token raises the rate limit from 60/hr to 5000/hr
    req = urllib.request.Request(API + path, headers={"User-Agent": "repo-stats-cli"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read())
            link_header = resp.getheader("Link")
            return body, link_header
    except urllib.error.HTTPError as e:
        sys.exit(f"GitHub API error {e.code} on {path}: {e.reason}")


def _last_page_count(link_header):
    # // pagination trick: rel="last" page number is a cheap total-count stand-in without walking every page
    if not link_header:
        return 1
    match = re.search(r'page=(\d+)>; rel="last"', link_header)
    return int(match.group(1)) if match else 1


def get_stats(repo, token=None):
    info, _ = _get(f"/repos/{repo}", token)
    _, contrib_link = _get(f"/repos/{repo}/contributors?per_page=1&anon=true", token)
    issues, _ = _get(f"/search/issues?q=repo:{repo}+type:issue+state:open", token)
    prs, _ = _get(f"/search/issues?q=repo:{repo}+type:pr+state:open", token)

    return {
        "repo": repo,
        "stars": info["stargazers_count"],
        "forks": info["forks_count"],
        "language": info["language"],
        "created_at": info["created_at"],
        "contributors": _last_page_count(contrib_link),
        "open_issues": issues["total_count"],
        "open_prs": prs["total_count"],
    }


def main():
    parser = argparse.ArgumentParser(description="Print quick stats for a GitHub repo.")
    parser.add_argument("repo", help="owner/repo, e.g. torvalds/linux")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    stats = get_stats(args.repo, token)
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
