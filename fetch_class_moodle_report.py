#!/usr/bin/env python3
"""
Zero-Disk-Space API-Based Moodle Gradebook Generator
Course: Advanced Software Engineering (ASE)

Fetches student information and itemized autograder task grades directly from GitHub REST API over HTTPS
without cloning any repositories or consuming disk space.

Usage:
    python fetch_class_moodle_report.py [--org ClassroomAsignments] [--assignment git-github-prac-asignment]
"""

import os
import sys
import json
import csv
import subprocess
import urllib.request
import urllib.error

def get_gh_token():
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if token:
        return token
    try:
        res = subprocess.run("gh auth token", shell=True, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return None

def fetch_api(url, token=None):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "ASE-Autograder-Report-Tool")
    req.add_header("Accept", "application/vnd.github.v3+json")
    if token:
        req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status in [200, 201]:
                return json.loads(response.read().decode('utf-8'))
    except Exception:
        pass
    return None

def fetch_raw_content(repo_full_name, file_path, token=None):
    raw_url = f"https://raw.githubusercontent.com/{repo_full_name}/main/{file_path}"
    req = urllib.request.Request(raw_url)
    req.add_header("User-Agent", "ASE-Autograder-Report-Tool")
    if token:
        req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return response.read().decode('utf-8')
    except Exception:
        pass
    return None

def main():
    org_name = "ClassroomAsignments"
    assignment_prefix = "git-github-prac-asignment"

    if "--org" in sys.argv:
        try:
            org_name = sys.argv[sys.argv.index("--org") + 1]
        except IndexError:
            pass

    if "--assignment" in sys.argv:
        try:
            assignment_prefix = sys.argv[sys.argv.index("--assignment") + 1]
        except IndexError:
            pass

    moodle_file = "moodle_consolidated_grades.csv"
    token = get_gh_token()

    moodle_headers = [
        "Identifier",          # Moodle Student ID
        "Full Name", 
        "GitHub Username", 
        "Task 1 (15)", 
        "Task 2 (15)", 
        "Task 3 (20)", 
        "Task 4 (20)", 
        "Task 5 (15)", 
        "Task 6 (15)", 
        "Grade (100)", 
        "Percentage", 
        "Status",
        "Repository URL"
    ]

    print(f"==================================================")
    print(f"  ASE Zero-Disk API Moodle Gradebook Generator   ")
    print(f"==================================================")
    print(f"Organization: {org_name}")
    print(f"Assignment Prefix: {assignment_prefix}")
    print(f"Fetching student repos via GitHub REST API...\n")

    records = []
    target_repos = []
    
    # Query organization repos
    try:
        cmd = f'gh repo list {org_name} --limit 200 --json name,fullName,htmlUrl,isTemplate'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            repos_data = json.loads(res.stdout)
            for r in repos_data:
                r_name = r.get("name", "")
                is_tpl = r.get("isTemplate", False)
                # Exclude template repos and match student repo prefix
                if not is_tpl and r_name.lower() != "git_github-practice-asgnmt" and (r_name.startswith(f"{assignment_prefix}-") or r_name.startswith("git-github-prac-asignment-")):
                    target_repos.append({
                        "name": r_name,
                        "full_name": r.get("fullName", f"{org_name}/{r_name}"),
                        "html_url": r.get("htmlUrl", f"https://github.com/{org_name}/{r_name}")
                    })
    except Exception:
        pass

    if not target_repos:
        api_url = f"https://api.github.com/orgs/{org_name}/repos?per_page=100"
        repos_data = fetch_api(api_url, token)
        if isinstance(repos_data, list):
            for r in repos_data:
                r_name = r.get("name", "")
                is_tpl = r.get("is_template", False)
                if not is_tpl and r_name.lower() != "git_github-practice-asgnmt" and (r_name.startswith(f"{assignment_prefix}-") or r_name.startswith("git-github-prac-asignment-")):
                    target_repos.append({
                        "name": r_name,
                        "full_name": r.get("full_name"),
                        "html_url": r.get("html_url")
                    })

    if not target_repos:
        local_dir = "Student-testing" if os.path.exists("Student-testing") else "."
        for root, dirs, files in os.walk(local_dir):
            if "student_info.json" in files and "autograder.py" in files:
                r_name = os.path.basename(os.path.abspath(root))
                target_repos.append({
                    "name": r_name,
                    "full_name": f"{org_name}/{r_name}",
                    "html_url": f"https://github.com/{org_name}/{r_name}",
                    "local_path": root
                })

    if not target_repos:
        print(f"No student repositories found matching prefix '{assignment_prefix}-' in '{org_name}'.")
        return

    print(f"Found {len(target_repos)} student repository/repositories matching assignment.\n")

    for repo_info in target_repos:
        r_name = repo_info["name"]
        full_name = repo_info["full_name"]
        html_url = repo_info["html_url"]
        local_path = repo_info.get("local_path")

        student_name = "Unknown Student"
        sid = "UNKNOWN-ID"
        gh_user = r_name.replace(f"{assignment_prefix}-", "")

        info_json = None
        if local_path:
            try:
                with open(os.path.join(local_path, "student_info.json"), 'r', encoding='utf-8') as f:
                    info_json = json.load(f)
            except Exception:
                pass
        else:
            raw_info = fetch_raw_content(full_name, "student_info.json", token)
            if raw_info:
                try:
                    info_json = json.loads(raw_info)
                except Exception:
                    pass

        if info_json:
            student_name = str(info_json.get("full_name", student_name)).strip()
            sid = str(info_json.get("student_id", sid)).strip()
            gh_user = str(info_json.get("github_username", gh_user)).strip()

        task_scores = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        task_weights = {1: 15, 2: 15, 3: 20, 4: 20, 5: 15, 6: 15}
        
        if not local_path:
            runs_url = f"https://api.github.com/repos/{full_name}/actions/runs?per_page=1"
            runs_data = fetch_api(runs_url, token)
            if runs_data and "workflow_runs" in runs_data and len(runs_data["workflow_runs"]) > 0:
                latest_run = runs_data["workflow_runs"][0]
                jobs_url = latest_run.get("jobs_url")
                if jobs_url:
                    jobs_data = fetch_api(jobs_url, token)
                    if jobs_data and "jobs" in jobs_data and len(jobs_data["jobs"]) > 0:
                        job_steps = jobs_data["jobs"][0].get("steps", [])
                        for step in job_steps:
                            step_name = step.get("name", "")
                            step_conclusion = step.get("conclusion")
                            
                            for task_num in range(1, 7):
                                if f"Task {task_num}" in step_name:
                                    if step_conclusion == "success":
                                        task_scores[task_num] = task_weights[task_num]
                                    else:
                                        task_scores[task_num] = 0
        else:
            import importlib.util
            old_cwd = os.getcwd()
            os.chdir(local_path)
            try:
                spec = importlib.util.spec_from_file_location("local_autograder", "autograder.py")
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                checkers = {
                    1: getattr(mod, "check_task_1", None),
                    2: getattr(mod, "check_task_2", None),
                    3: getattr(mod, "check_task_3", None),
                    4: getattr(mod, "check_task_4", None),
                    5: getattr(mod, "check_task_5", None),
                    6: getattr(mod, "check_task_6", None),
                }
                for num, func in checkers.items():
                    if func:
                        try:
                            score, _ = func()
                            task_scores[num] = int(score)
                        except Exception:
                            task_scores[num] = 0
            except Exception:
                pass
            os.chdir(old_cwd)

        total_score = sum(task_scores.values())
        pct = f"{int(total_score)}%"
        status = "PASSED" if total_score == 100 else ("PARTIAL" if total_score > 0 else "FAILED")

        records.append([
            sid,
            student_name,
            gh_user,
            task_scores[1],
            task_scores[2],
            task_scores[3],
            task_scores[4],
            task_scores[5],
            task_scores[6],
            total_score,
            pct,
            status,
            html_url
        ])

        print(f"  ✔ Student: {student_name:20s} | ID: {sid:12s} | Score: {total_score:3d}/100 pts | Repo: {html_url}")

    with open(moodle_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(moodle_headers)
        writer.writerows(records)

    print(f"\n==================================================")
    print(f"  CONSOLIDATED MOODLE GRADEBOOK GENERATED  ")
    print(f"==================================================")
    print(f"File Saved: {os.path.abspath(moodle_file)}")
    print(f"Disk Space Consumed: ~{os.path.getsize(moodle_file) // 1024 + 1} KB")
    print(f"==================================================\n")

if __name__ == "__main__":
    main()
