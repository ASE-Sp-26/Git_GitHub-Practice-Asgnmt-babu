#!/usr/bin/env python3
"""
Zero-Disk-Space API-Based Moodle Gradebook & PDF Evaluation Generator
Course: Advanced Software Engineering (ASE)

Fetches student information, itemized autograder grades, and builds both:
1. Moodle CSV Gradebook: moodle_consolidated_grades.csv
2. Individual Student Evaluation PDFs: evaluation_reports/<StudentID>_<StudentName>_Evaluation.pdf

Usage:
    python fetch_class_moodle_report.py [--org ClassroomAsignments] [--assignment git-github-prac-asignment]
"""

import os
import sys
import json
import csv
import re
import subprocess
import datetime
import urllib.request
import urllib.error

class RobustPDFWriter:
    """Zero-dependency, pure-Python valid PDF 1.4 Document Generator."""
    def __init__(self, filename):
        self.filename = filename

    def build_student_pdf(self, name, sid, gh_user, task_data, total_score, max_possible):
        pct = int((total_score / max_possible) * 100) if max_possible > 0 else 0
        status_str = "PASSED" if total_score == max_possible else ("PARTIAL" if total_score > 0 else "FAILED")
        date_str = datetime.datetime.now().strftime("%B %d, %Y")

        stream_cmds = []
        
        # Header Box
        stream_cmds.append("0.1 0.2 0.4 rg 40 730 532 45 re f")
        stream_cmds.append("BT /F1 16 Tf 1 1 1 rg 55 754 Td (Advanced Software Engineering - Evaluation Report) Tj ET")
        stream_cmds.append("BT /F2 9 Tf 0.9 0.9 0.9 rg 55 738 Td (Course Code: ASE-Sp26 | Assignment: Git & GitHub Practice) Tj ET")

        # Student Details Box
        stream_cmds.append("0.96 0.96 0.98 rg 40 650 532 65 re f")
        stream_cmds.append("0.8 0.8 0.85 RG 1 w 40 650 532 65 re s")
        
        stream_cmds.append("BT /F1 10 Tf 0 0 0 rg 55 695 Td (Student Name:) Tj ET")
        stream_cmds.append(f"BT /F2 10 Tf 0.2 0.2 0.2 rg 150 695 Td ({self._clean(name)}) Tj ET")
        stream_cmds.append("BT /F1 10 Tf 0 0 0 rg 330 695 Td (Student ID:) Tj ET")
        stream_cmds.append(f"BT /F2 10 Tf 0.2 0.2 0.2 rg 420 695 Td ({self._clean(sid)}) Tj ET")

        stream_cmds.append("BT /F1 10 Tf 0 0 0 rg 55 668 Td (GitHub Username:) Tj ET")
        stream_cmds.append(f"BT /F2 10 Tf 0.2 0.2 0.2 rg 150 668 Td (@{self._clean(gh_user)}) Tj ET")
        stream_cmds.append("BT /F1 10 Tf 0 0 0 rg 330 668 Td (Date Evaluated:) Tj ET")
        stream_cmds.append(f"BT /F2 10 Tf 0.2 0.2 0.2 rg 420 668 Td ({date_str}) Tj ET")

        # Final Scorecard Box
        if status_str == "PASSED":
            stream_cmds.append("0.9 0.96 0.9 rg 40 580 532 55 re f")
            stream_cmds.append("0.2 0.6 0.2 RG 1.5 w 40 580 532 55 re s")
            stream_cmds.append(f"BT /F1 13 Tf 0.1 0.4 0.1 rg 55 605 Td (FINAL GRADE: {total_score} / {max_possible} Points [{pct}%]) Tj ET")
            stream_cmds.append("BT /F1 13 Tf 0.1 0.4 0.1 rg 420 605 Td (STATUS: PASSED) Tj ET")
        else:
            stream_cmds.append("0.98 0.91 0.91 rg 40 580 532 55 re f")
            stream_cmds.append("0.7 0.2 0.2 RG 1.5 w 40 580 532 55 re s")
            stream_cmds.append(f"BT /F1 13 Tf 0.6 0.1 0.1 rg 55 605 Td (FINAL GRADE: {total_score} / {max_possible} Points [{pct}%]) Tj ET")
            stream_cmds.append(f"BT /F1 13 Tf 0.6 0.1 0.1 rg 420 605 Td (STATUS: {status_str}) Tj ET")

        # Task Breakdown Header
        stream_cmds.append("BT /F1 12 Tf 0 0 0 rg 40 550 Td (Task Breakdown & Feedback:) Tj ET")
        
        # Table Header Box
        stream_cmds.append("0.2 0.3 0.5 rg 40 520 532 20 re f")
        stream_cmds.append("BT /F1 9 Tf 1 1 1 rg 50 526 Td (Task Title) Tj ET")
        stream_cmds.append("BT /F1 9 Tf 1 1 1 rg 340 526 Td (Score) Tj ET")
        stream_cmds.append("BT /F1 9 Tf 1 1 1 rg 450 526 Td (Status) Tj ET")

        y = 490
        for t_title, score, max_pts, feedback in task_data:
            t_status = "PASS" if score == max_pts else ("PARTIAL" if score > 0 else "FAIL")
            
            stream_cmds.append(f"0.97 0.97 0.97 rg 40 {y-5} 532 25 re f")
            stream_cmds.append(f"0.85 0.85 0.85 RG 0.5 w 40 {y-5} 532 25 re s")

            stream_cmds.append(f"BT /F1 9 Tf 0 0 0 rg 50 {y+5} Td ({self._clean(t_title)}) Tj ET")
            stream_cmds.append(f"BT /F2 9 Tf 0.2 0.2 0.2 rg 345 {y+5} Td ({score}/{max_pts} pts) Tj ET")
            
            stat_color = "0 0.5 0" if t_status == "PASS" else "0.7 0 0"
            stream_cmds.append(f"BT /F1 9 Tf {stat_color} rg 455 {y+5} Td ({t_status}) Tj ET")
            
            fb_y = y - 18
            for fb_item in feedback[:2]:
                cleaned_fb = self._clean(fb_item)
                stream_cmds.append(f"BT /F2 8 Tf 0.3 0.3 0.3 rg 60 {fb_y} Td (- {cleaned_fb[:80]}) Tj ET")
                fb_y -= 11
            
            y -= 45

        # Footer
        stream_cmds.append("0.8 0.8 0.8 RG 1 w 40 45 m 572 45 l S")
        stream_cmds.append("BT /F2 8 Tf 0.5 0.5 0.5 rg 40 32 Td (Generated automatically by ASE Autograder System. Official Record.) Tj ET")

        stream_data = "\n".join(stream_cmds).encode('latin1', errors='replace')

        pdf_bytes = bytearray()
        pdf_bytes.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        offsets = []
        
        def add_obj(body):
            offsets.append(len(pdf_bytes))
            obj_id = len(offsets)
            pdf_bytes.extend(f"{obj_id} 0 obj\n".encode('latin1'))
            if isinstance(body, bytes):
                pdf_bytes.extend(body)
            else:
                pdf_bytes.extend(body.encode('latin1'))
            pdf_bytes.extend(b"\nendobj\n")
            return obj_id

        add_obj("<</Type /Catalog /Pages 2 0 R>>")
        add_obj("<</Type /Pages /Kids [3 0 R] /Count 1>>")
        add_obj("<</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources 4 0 R /Contents 5 0 R>>")
        add_obj("<</Font <</F1 <</Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold>> /F2 <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>>> >>")
        add_obj(f"<</Length {len(stream_data)}>>\nstream\n".encode('latin1') + stream_data + b"\nendstream")

        xref_pos = len(pdf_bytes)
        pdf_bytes.extend(f"xref\n0 {len(offsets) + 1}\n0000000000 65535 f \n".encode('latin1'))
        for off in offsets:
            pdf_bytes.extend(f"{off:010d} 00000 n \n".encode('latin1'))
        
        pdf_bytes.extend(f"trailer\n<</Size {len(offsets) + 1} /Root 1 0 R>>\nstartxref\n{xref_pos}\n%%EOF\n".encode('latin1'))

        with open(self.filename, 'wb') as f:
            f.write(pdf_bytes)

    def _clean(self, text):
        clean_text = re.sub(r'\x1b\[[0-9;]*m', '', str(text))
        return clean_text.replace('\\', '/').replace('(', '[').replace(')', ']')


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
    pdf_dir = "evaluation_reports"
    os.makedirs(pdf_dir, exist_ok=True)
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
    print(f"  ASE Zero-Disk API Moodle & PDF Report Suite    ")
    print(f"==================================================")
    print(f"Organization: {org_name}")
    print(f"Assignment Prefix: {assignment_prefix}")
    print(f"Fetching student repos & generating PDF evaluation sheets...\n")

    records = []
    target_repos = []
    
    # Query organization repos via gh CLI
    try:
        cmd = f'gh repo list {org_name} --limit 200 --json name,fullName,htmlUrl,isTemplate'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            repos_data = json.loads(res.stdout)
            for r in repos_data:
                r_name = r.get("name", "")
                is_tpl = r.get("isTemplate", False)
                if not is_tpl and r_name.lower() != "git_github-practice-asgnmt" and (r_name.startswith(f"{assignment_prefix}-") or r_name.startswith("git-github-prac-asignment-")):
                    target_repos.append({
                        "name": r_name,
                        "full_name": r.get("fullName", f"{org_name}/{r_name}"),
                        "html_url": r.get("htmlUrl", f"https://github.com/{org_name}/{r_name}")
                    })
    except Exception:
        pass

    # Query via REST API
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

    # Local directory scanning fallback
    if not target_repos and os.path.exists("Student-testing"):
        print("Scanning local Student-testing directory...")
        for root, dirs, files in os.walk("Student-testing"):
            if "student_info.json" in files and "autograder.py" in files:
                r_name = os.path.basename(os.path.abspath(root))
                target_repos.append({
                    "name": r_name,
                    "full_name": f"{org_name}/{r_name}",
                    "html_url": f"https://github.com/{org_name}/{r_name}",
                    "local_path": root
                })

    if not target_repos:
        print(f"⚠️ No student repositories found matching prefix '{assignment_prefix}-' in '{org_name}'.")
        print("Tip: If running in GitHub Codespaces, please run 'gh auth login' once to grant organization read access.")
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

        # Strict check: Skip un-edited placeholder template records
        if student_name == "YOUR NAME HERE" or sid == "YOUR STUDENT ID HERE" or r_name.lower() == "git_github-practice-asgnmt":
            continue

        task_scores = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        task_weights = {1: 15, 2: 15, 3: 20, 4: 20, 5: 15, 6: 15}
        task_titles = {
            1: "Task 1: Git Config & Student Info",
            2: "Task 2: .gitignore Configuration",
            3: "Task 3: Branching & Calculator",
            4: "Task 4: Merge Conflict Resolution",
            5: "Task 5: Git Stashing & Tagging",
            6: "Task 6: GitHub Reflection",
        }
        task_details = []
        
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
            
            for t_num in range(1, 7):
                max_p = task_weights[t_num]
                sc = task_scores[t_num]
                msg = ["PASS: Autograder check completed."] if sc == max_p else ["FAIL: Requirement incomplete."]
                task_details.append((task_titles[t_num], sc, max_p, msg))
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
                            score, fb = func()
                            task_scores[num] = int(score)
                            task_details.append((task_titles[num], int(score), task_weights[num], fb))
                        except Exception:
                            task_scores[num] = 0
                            task_details.append((task_titles[num], 0, task_weights[num], ["FAIL: Error executing check."]))
            except Exception:
                pass
            os.chdir(old_cwd)

        total_score = sum(task_scores.values())
        max_possible = 100
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

        # Generate Individual PDF Report for every student
        clean_sid = "".join(c for c in sid if c.isalnum() or c in ['-', '_'])
        clean_name = "".join(c for c in student_name if c.isalnum() or c == '_').replace(' ', '_')
        pdf_filename = os.path.join(pdf_dir, f"{clean_sid}_{clean_name}_Evaluation.pdf")
        
        pdf_writer = RobustPDFWriter(pdf_filename)
        pdf_writer.build_student_pdf(student_name, sid, gh_user, task_details, total_score, max_possible)

        print(f"  ✔ Student: {student_name:20s} | ID: {sid:12s} | Score: {total_score:3d}/100 pts | PDF: {os.path.basename(pdf_filename)}")

    if not records:
        print("⚠️ No valid student records found. If running in Codespaces, please run 'gh auth login' once to allow API listing.")
        return

    with open(moodle_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(moodle_headers)
        writer.writerows(records)

    print(f"\n==================================================")
    print(f"  CONSOLIDATED MOODLE CSV & STUDENT PDFs GENERATED ")
    print(f"==================================================")
    print(f"1. Moodle Gradebook CSV : {os.path.abspath(moodle_file)}")
    print(f"2. Student PDF Reports  : {os.path.abspath(pdf_dir)}/")
    print(f"Disk Space Consumed     : ~{os.path.getsize(moodle_file) // 1024 + 1} KB")
    print(f"==================================================\n")

if __name__ == "__main__":
    main()
