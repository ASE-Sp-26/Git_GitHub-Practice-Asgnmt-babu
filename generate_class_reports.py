#!/usr/bin/env python3
"""
Master Class Report & Moodle Feedback Text Generator
Course: Advanced Software Engineering (ASE)

Generates:
1. Moodle-Compatible Consolidated Gradebook: evaluation_reports/moodle_consolidated_grades.csv
2. Single Moodle Text Feedback Comments File: evaluation_reports/moodle_student_feedback_comments.txt

Fetches student data from:
- Pull Requests submitted to the repository (GitHub API / gh pr list)
- Local student folders (./Student-testing/*)

Usage:
    python generate_class_reports.py [--dir ./Student-testing] [--org ClassroomAsignments]
"""

import os
import sys
import json
import csv
import re
import datetime
import subprocess
import urllib.request
import urllib.error
import importlib.util
import shutil

def get_gh_executable():
    path = shutil.which("gh")
    if path:
        return f'"{path}"'
    possible_paths = [
        r"C:\Program Files\GitHub CLI\gh.exe",
        r"C:\Program Files (x86)\GitHub CLI\gh.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\GitHub CLI\gh.exe"),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return f'"{p}"'
    return "gh"

def get_gh_token():
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if token:
        return token
    try:
        gh_bin = get_gh_executable()
        res = subprocess.run(f"{gh_bin} auth token", shell=True, capture_output=True, text=True)
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

def fetch_raw_content(repo_full_name, file_path, token=None, ref="main"):
    raw_url = f"https://raw.githubusercontent.com/{repo_full_name}/{ref}/{file_path}"
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

def load_autograder_module(repo_path):
    autograder_file = os.path.join(repo_path, "autograder.py")
    if not os.path.exists(autograder_file):
        return None
    try:
        spec = importlib.util.spec_from_file_location("student_autograder", autograder_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        print(f"Error loading autograder from {repo_path}: {e}")
        return None

def clean_ansi(text):
    if not text:
        return ""
    return re.sub(r'(\x1b|\^\[)\[[0-9;]*[a-zA-Z]', '', str(text)).strip()


def main():
    target_dir = "."
    org_name = "ClassroomAsignments"
    assignment_prefix = "git-github-prac-asignment"

    if "--dir" in sys.argv:
        try:
            target_dir = sys.argv[sys.argv.index("--dir") + 1]
        except IndexError:
            pass

    if "--org" in sys.argv:
        try:
            org_name = sys.argv[sys.argv.index("--org") + 1]
        except IndexError:
            pass

    output_dir = "evaluation_reports"
    os.makedirs(output_dir, exist_ok=True)
    moodle_file = os.path.join(output_dir, "moodle_consolidated_grades.csv")
    feedback_txt_file = os.path.join(output_dir, "moodle_student_feedback_comments.txt")
    
    token = get_gh_token()
    gh_bin = get_gh_executable()

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
        "Status"
    ]

    moodle_records = []
    student_repos = []
    seen_identifiers = set()

    # 1. Discover Pull Requests submitted to the main repository (PR Model - Priority 1)
    current_repo_full = f"{org_name}/Git_GitHub-Practice-Asgnmt"
    try:
        res = subprocess.run(f"{gh_bin} repo view --json fullName", shell=True, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            current_repo_full = json.loads(res.stdout).get("fullName", current_repo_full)
    except Exception:
        pass

    try:
        cmd = f'{gh_bin} pr list --state all --limit 200 --json number,author,headRefName,headRepository,headRepositoryOwner'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            prs_data = json.loads(res.stdout)
            for pr in prs_data:
                author_login = pr.get("author", {}).get("login", "")
                head_repo_name = pr.get("headRepository", {}).get("name")
                head_owner = pr.get("headRepositoryOwner", {}).get("login") or author_login
                head_ref = pr.get("headRefName", "main")
                full_head_repo = f"{head_owner}/{head_repo_name}" if head_repo_name else current_repo_full
                r_name = f"pr-{pr.get('number')}-{author_login}"
                if author_login and not any(item.get("pr_num") == pr.get("number") for item in student_repos):
                    student_repos.append({
                        "name": r_name,
                        "full_name": full_head_repo,
                        "pr_ref": head_ref,
                        "pr_num": pr.get("number"),
                        "gh_user": author_login,
                        "html_url": f"https://github.com/{current_repo_full}/pull/{pr.get('number')}"
                    })
    except Exception:
        pass

    # 2. Discover local student directories and match with PR entries or add as standalone
    for scan_dir in [target_dir, "Student-testing", "./Student-testing", "../Student Repos", "Student Repos"]:
        if os.path.exists(scan_dir):
            for root, dirs, files in os.walk(scan_dir):
                if "student_info.json" in files and "autograder.py" in files:
                    info_file = os.path.join(root, "student_info.json")
                    try:
                        with open(info_file, 'r', encoding='utf-8') as f:
                            info_chk = json.load(f)
                            s_name = str(info_chk.get("full_name", "")).strip().upper()
                            gh_user_chk = str(info_chk.get("github_username", "")).strip().lower()
                            sid_chk = str(info_chk.get("student_id", "")).strip().lower()
                            if "YOUR NAME" in s_name or s_name == "":
                                continue
                    except Exception:
                        continue

                    r_name = os.path.basename(os.path.abspath(root))
                    if r_name.lower() == "git_github-practice-asgnmt":
                        continue

                    matched = False
                    for item in student_repos:
                        if item.get("gh_user", "").lower() == gh_user_chk and not item.get("local_path"):
                            item["local_path"] = root
                            matched = True
                            break
                    
                    if not matched and not any(item.get("name") == r_name or item.get("local_path") == root for item in student_repos):
                        student_repos.append({
                            "name": r_name,
                            "full_name": f"{org_name}/{r_name}",
                            "local_path": root
                        })

    if token and not any("pr_ref" in item for item in student_repos):
        prs_url = f"https://api.github.com/repos/{current_repo_full}/pulls?state=all&per_page=100"
        prs_data = fetch_api(prs_url, token)
        if isinstance(prs_data, list):
            for pr in prs_data:
                author_login = pr.get("user", {}).get("login", "")
                head_ref = pr.get("head", {}).get("ref", "main")
                head_repo = pr.get("head", {}).get("repo", {}).get("full_name", current_repo_full)
                r_name = f"pr-{author_login}"
                if author_login and not any(item.get("gh_user") == author_login for item in student_repos):
                    student_repos.append({
                        "name": r_name,
                        "full_name": head_repo,
                        "pr_ref": head_ref,
                        "pr_num": pr.get("number"),
                        "gh_user": author_login,
                        "html_url": pr.get("html_url")
                    })

    if not student_repos:
        print(f"⚠️ No student submissions/repositories found in '{target_dir}', PRs, or organization '{org_name}'.")
        return

    print(f"==================================================")
    print(f"  ASE Master Class Report & Text Feedback Suite   ")
    print(f"==================================================\n")
    print(f"Processing {len(student_repos)} student submission(s)/repository/repositories...\n")

    task_weights = {1: 15, 2: 15, 3: 20, 4: 20, 5: 15, 6: 15}
    task_titles = {
        1: "Task 1: Git Config & Student Info",
        2: "Task 2: .gitignore Configuration",
        3: "Task 3: Branching & Calculator",
        4: "Task 4: Merge Conflict Resolution",
        5: "Task 5: Git Stashing & Tagging",
        6: "Task 6: GitHub Reflection",
    }

    feedback_blocks = []
    header_block = (
        "================================================================================\n"
        "  ADVANCED SOFTWARE ENGINEERING (ASE) - STUDENT EVALUATION FEEDBACK REPORT\n"
        "  Assignment: Git & GitHub Practice Assignment\n"
        f"  Date Generated: {datetime.datetime.now().strftime('%B %d, %Y')}\n"
        "================================================================================\n\n"
    )
    feedback_blocks.append(header_block)

    for repo_info in student_repos:
        local_path = repo_info.get("local_path")
        full_name = repo_info.get("full_name")
        r_name = repo_info.get("name", "")
        pr_ref = repo_info.get("pr_ref", "main")
        pr_num = repo_info.get("pr_num")

        gh_user = repo_info.get("gh_user", r_name)
        for prefix in [f"{assignment_prefix}-", "git-github-prac-asignment-", "github-starter-course-", "pr-"]:
            if r_name.startswith(prefix):
                gh_user = r_name[len(prefix):]
                break

        name = f"Student ({gh_user})"
        sid = gh_user

        info_json = None
        if local_path:
            try:
                with open(os.path.join(local_path, "student_info.json"), 'r', encoding='utf-8') as f:
                    info_json = json.load(f)
            except Exception:
                pass
        else:
            raw_info = fetch_raw_content(full_name, "student_info.json", token, ref=pr_ref)
            if raw_info:
                try:
                    info_json = json.loads(raw_info)
                except Exception:
                    pass

        if info_json:
            parsed_name = str(info_json.get("full_name", "")).strip()
            parsed_sid = str(info_json.get("student_id", "")).strip()
            parsed_gh = str(info_json.get("github_username", "")).strip()

            if parsed_name and "YOUR NAME" not in parsed_name.upper():
                name = parsed_name
            if parsed_sid and "YOUR STUDENT ID" not in parsed_sid.upper():
                sid = parsed_sid
            if parsed_gh and "YOUR GITHUB" not in parsed_gh.upper():
                gh_user = parsed_gh
        
        comments_data = None
        if pr_num and not local_path:
            try:
                cmd = f'{gh_bin} pr view {pr_num} --json comments'
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    comments_data = json.loads(res.stdout).get("comments", [])
            except Exception:
                pass

            if not comments_data and token:
                comments_url = f"https://api.github.com/repos/{current_repo_full}/issues/{pr_num}/comments"
                comments_data = fetch_api(comments_url, token)

            if comments_data and isinstance(comments_data, list):
                for comment in reversed(comments_data):
                    body = clean_ansi(comment.get("body", ""))
                    if "Assignment Evaluation Results" in body or "TOTAL SCORE:" in body:
                        m_info = re.search(r'student_info\.json valid \(([^,]+),\s*([^,]+),\s*@([^)]+)\)', body)
                        if m_info:
                            name = m_info.group(1).strip()
                            sid = m_info.group(2).strip()
                            gh_user = m_info.group(3).strip()
                        break

        # Exclude template repository itself if name is placeholder
        if r_name.lower() == "git_github-practice-asgnmt" and local_path:
            continue

        if sid in seen_identifiers:
            continue
        seen_identifiers.add(sid)

        task_details = []
        task_scores = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        total_score = 0
        max_possible = 100

        if local_path:
            old_cwd = os.getcwd()
            os.chdir(local_path)
            mod = load_autograder_module(".")
            checkers = {
                1: getattr(mod, "check_task_1", None),
                2: getattr(mod, "check_task_2", None),
                3: getattr(mod, "check_task_3", None),
                4: getattr(mod, "check_task_4", None),
                5: getattr(mod, "check_task_5", None),
                6: getattr(mod, "check_task_6", None),
            }
            for num, func in checkers.items():
                max_pts = task_weights[num]
                if func:
                    try:
                        score, feedback = func()
                        score = int(score)
                    except Exception as e:
                        score = 0
                        feedback = [f"FAIL: Error executing check: {e}"]
                else:
                    score = 0
                    feedback = ["FAIL: Checker function not found."]

                task_scores[num] = score
                task_details.append((task_titles[num], score, max_pts, feedback))
            os.chdir(old_cwd)
        else:
            parsed_from_comment = False
            if comments_data and isinstance(comments_data, list):
                for comment in reversed(comments_data):
                    body = clean_ansi(comment.get("body", ""))
                    if "Assignment Evaluation Results" in body or "TOTAL SCORE:" in body:
                        for task_num in range(1, 7):
                            max_pts = task_weights[task_num]
                            score = 0
                            # Match Task N score e.g. "Task 1: Git Config & Student Info (15 pts) \n Score: 15/15 pts" or "Task 1 ... (15/15 pts)"
                            m = re.search(rf'Task {task_num}[^\n]*?\n\s*Score:\s*(\d+)/(\d+)', body, re.IGNORECASE)
                            if not m:
                                m = re.search(rf'Task {task_num}[^\n]*?\((\d+)/(\d+)\s*pts\)', body, re.IGNORECASE)
                            if not m:
                                m = re.search(rf'Task {task_num}[^\n]*?:[^\n]*?(\d+)/(\d+)', body, re.IGNORECASE)

                            if m:
                                score = int(m.group(1))

                            fb_m = re.search(rf'Task {task_num}:[^\n]*\n((?:[ \t]*(?:└─|-|•)[^\n]*\n?)*)', body)
                            fb_lines = []
                            if fb_m:
                                fb_lines = [clean_ansi(l) for l in fb_m.group(1).splitlines() if clean_ansi(l)]
                            if not fb_lines:
                                fb_lines = ["PASS: Autograder check completed."] if score == max_pts else ["FAIL: Requirement incomplete."]
                            
                            task_scores[task_num] = score
                            task_details.append((task_titles[task_num], score, max_pts, fb_lines))
                        parsed_from_comment = True
                        break

            if not parsed_from_comment:
                # Query GitHub Actions workflow runs for remote student repo / PR
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

                for t_num in range(1, 7):
                    max_p = task_weights[t_num]
                    sc = task_scores[t_num]
                    msg = ["PASS: Autograder check completed."] if sc == max_p else ["FAIL: Requirement incomplete."]
                    task_details.append((task_titles[t_num], sc, max_p, msg))

        total_score = sum(task_scores.values())
        pct = f"{int((total_score / max_possible) * 100)}%"
        status = "PASSED" if total_score == max_possible else ("PARTIAL" if total_score > 0 else "FAILED")

        moodle_records.append([
            sid,
            name,
            gh_user,
            task_scores[1],
            task_scores[2],
            task_scores[3],
            task_scores[4],
            task_scores[5],
            task_scores[6],
            total_score,
            pct,
            status
        ])

        # Build bulleted text block for student feedback
        student_txt = []
        student_txt.append("--------------------------------------------------------------------------------")
        student_txt.append(f"STUDENT: {name} | ID: {sid} | GitHub: @{gh_user}")
        student_txt.append(f"FINAL GRADE: {total_score} / {max_possible} pts [{pct}] | STATUS: {status}")
        student_txt.append("--------------------------------------------------------------------------------")

        for t_title, sc, max_p, fb_list in task_details:
            t_stat = "PASS" if sc == max_p else ("PARTIAL" if sc > 0 else "FAIL")
            student_txt.append(f"• {t_title} ({sc}/{max_p} pts) [{t_stat}]")
            for fb_item in fb_list:
                clean_fb = clean_ansi(fb_item)
                student_txt.append(f"  - {clean_fb}")
        
        student_txt.append("\n")
        feedback_blocks.append("\n".join(student_txt))

        print(f"  ✔ Student: {name:20s} ({sid:15s}) | Score: {total_score:3d}/100 pts | Status: {status}")

    # Write Moodle Consolidated CSV
    with open(moodle_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(moodle_headers)
        writer.writerows(moodle_records)

    # Write Consolidated Moodle Student Text Feedback File
    with open(feedback_txt_file, 'w', encoding='utf-8') as f:
        f.write("".join(feedback_blocks))

    print(f"\n==================================================")
    print(f"  OUTPUTS GENERATED SUCCESSFULLY  ")
    print(f"==================================================")
    print(f"1. Moodle Gradebook CSV          : {os.path.abspath(moodle_file)}")
    print(f"2. Moodle Text Feedback Comments : {os.path.abspath(feedback_txt_file)}")
    print(f"==================================================\n")

if __name__ == "__main__":
    main()
