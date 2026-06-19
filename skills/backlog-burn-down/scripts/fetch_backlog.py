#!/usr/bin/env python3
"""
fetch_backlog.py — Fetch unassigned Todo issues from a GitHub Projects v2 board.

Usage:
    python3 fetch_backlog.py [--org ORG] [--repo REPO] [--project N] [--pretty]

Auto-detects org and repo from the current git remote if not provided.
Lists available projects for the org if --project is not provided.

Output: JSON array of issues, sorted by priority then updatedAt ascending.
"""

import argparse
import json
import subprocess
import sys

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "": 4}

GRAPHQL_QUERY = """
query($org: String!, $num: Int!, $cursor: String) {
  organization(login: $org) {
    projectV2(number: $num) {
      id
      fields(first: 20) {
        nodes {
          ... on ProjectV2SingleSelectField {
            id
            name
            options { id name }
          }
        }
      }
      items(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                field { ... on ProjectV2SingleSelectField { name } }
                name
              }
            }
          }
          content {
            ... on Issue {
              number title body url state updatedAt
              assignees(first: 10) { nodes { login } }
              labels(first: 20) { nodes { name } }
            }
          }
        }
      }
    }
  }
}
"""


def run(cmd, capture=True):
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"Command failed: {cmd}")
    return result.stdout.strip() if capture else None


def resolve_org_repo():
    try:
        return run("gh repo view --json owner,name --jq '\"\\(.owner.login)/\\(.name)\"'").strip('"')
    except RuntimeError:
        return None


def resolve_my_login():
    try:
        return run("gh api user --jq '.login'")
    except RuntimeError:
        return None


def list_projects(org):
    try:
        output = run(f"gh project list --owner {org} --format json")
        projects = json.loads(output).get("projects", [])
        return projects
    except (RuntimeError, json.JSONDecodeError):
        return []


def fetch_all_items(org, project_number):
    items = []
    project_id = None
    field_meta = {}
    cursor = ""

    while True:
        result = subprocess.run(
            ["gh", "api", "graphql",
             "-f", f"query={GRAPHQL_QUERY}",
             "-F", f"org={org}",
             "-F", f"num={project_number}",
             "-f", f"cursor={cursor}"],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())

        data = json.loads(result.stdout)
        project = data["data"]["organization"]["projectV2"]
        project_id = project["id"]

        # Capture field metadata (Status field options) on first page
        if not field_meta:
            for field in project["fields"]["nodes"]:
                if field.get("name") == "Status":
                    field_meta["status_field_id"] = field["id"]
                    field_meta["status_options"] = {
                        opt["name"]: opt["id"] for opt in field.get("options", [])
                    }

        page = project["items"]
        items.extend(page["nodes"])

        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    return items, project_id, field_meta


def extract_field(item, field_name):
    for fv in item.get("fieldValues", {}).get("nodes", []):
        if fv.get("field", {}).get("name") == field_name:
            return fv.get("name", "")
    return ""


def priority_rank(issue):
    labels = [l["name"].lower() for l in issue.get("labels", {}).get("nodes", [])]
    for label in labels:
        for key in PRIORITY_ORDER:
            if key and key in label:
                return PRIORITY_ORDER[key]
    return PRIORITY_ORDER[""]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description="Fetch unassigned Todo issues from GitHub Projects v2")
    parser.add_argument("--org",     help="GitHub org (auto-detected from git remote if omitted)")
    parser.add_argument("--repo",    help="GitHub repo name (auto-detected if omitted)")
    parser.add_argument("--project", type=int, help="Project number (prompted if omitted)")
    parser.add_argument("--pretty",  action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    # Resolve org/repo
    org_repo = resolve_org_repo()
    if org_repo:
        auto_org, auto_repo = org_repo.split("/", 1)
    else:
        auto_org, auto_repo = None, None

    org  = args.org  or auto_org
    repo = args.repo or auto_repo

    if not org:
        print("ERROR: Could not detect org from git remote. Pass --org explicitly.", file=sys.stderr)
        sys.exit(1)

    # Resolve project number
    project_number = args.project
    if not project_number:
        projects = list_projects(org)
        if len(projects) == 1:
            project_number = projects[0]["number"]
            print(f"Auto-selected project #{project_number}: {projects[0]['title']}", file=sys.stderr)
        elif projects:
            print("Available projects:", file=sys.stderr)
            for p in projects:
                print(f"  #{p['number']}  {p['title']}", file=sys.stderr)
            print("ERROR: Multiple projects found. Pass --project N to select one.", file=sys.stderr)
            sys.exit(1)
        else:
            print("ERROR: No projects found for this org. Pass --project N explicitly.", file=sys.stderr)
            sys.exit(1)

    # Resolve current user login
    my_login = resolve_my_login()

    # Fetch all items
    try:
        all_items, project_id, field_meta = fetch_all_items(org, project_number)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Filter: Status=Todo, state=OPEN, assignees empty or includes me
    todo_issues = []
    for item in all_items:
        content = item.get("content", {})
        if not content:
            continue
        if content.get("state") != "OPEN":
            continue
        status = extract_field(item, "Status")
        if status != "Todo":
            continue
        assignees = [a["login"] for a in content.get("assignees", {}).get("nodes", [])]
        if assignees and (my_login not in assignees):
            continue

        labels = [l["name"] for l in content.get("labels", {}).get("nodes", [])]
        todo_issues.append({
            "item_id":      item["id"],
            "project_id":   project_id,
            "number":       content["number"],
            "title":        content["title"],
            "body":         content["body"],
            "url":          content["url"],
            "updatedAt":    content["updatedAt"],
            "assignees":    assignees,
            "labels":       labels,
            "status":       status,
            "field_meta":   field_meta,
        })

    # Sort: priority asc, then updatedAt asc
    todo_issues.sort(key=lambda i: (priority_rank(i), i["updatedAt"]))

    output = {
        "org":            org,
        "repo":           repo,
        "project_number": project_number,
        "my_login":       my_login,
        "total_scanned":  len(all_items),
        "issues":         todo_issues,
    }

    indent = 2 if args.pretty else None
    print(json.dumps(output, indent=indent))


if __name__ == "__main__":
    main()
