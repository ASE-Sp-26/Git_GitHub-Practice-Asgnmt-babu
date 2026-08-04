#!/usr/bin/env python3
"""
Autograder Script for Git & GitHub Practice Assignment
This script evaluates Tasks 1 through 6 locally and in GitHub Classroom CI pipelines.

Usage:
    python autograder.py [--task N]
"""

import sys
import os
import json
import re
import subprocess
import importlib.util

TOTAL_POINTS = 100
TASK_WEIGHTS = {
    1: 15,
    2: 15,
    3: 20,
    4: 20,
    5: 15,
    6: 15
}

USE_COLOR = sys.stdout.isatty() and "--no-color" not in sys.argv

class Colors:
    GREEN = '\033[92m' if USE_COLOR else ''
    RED = '\033[91m' if USE_COLOR else ''
    YELLOW = '\033[93m' if USE_COLOR else ''
    BLUE = '\033[94m' if USE_COLOR else ''
    BOLD = '\033[1m' if USE_COLOR else ''
    RESET = '\033[0m' if USE_COLOR else ''


def run_cmd(cmd):
    """Utility to execute shell/git commands and return (stdout, stderr, returncode)."""
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return res.stdout.strip(), res.stderr.strip(), res.returncode
    except Exception as e:
        return "", str(e), 1

def check_task_1():
    """Task 1: Student info in student_info.json and Git config (15 pts)."""
    score = 0
    feedback = []
    
    info_path = "student_info.json"
    if not os.path.exists(info_path):
        return 0, ["FAIL: student_info.json file does not exist."]
    
    try:
        with open(info_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        name = data.get("full_name", "").strip()
        sid = data.get("student_id", "").strip()
        gh_user = data.get("github_username", "").strip()
        
        if not name or "YOUR NAME" in name.upper():
            feedback.append("FAIL: 'full_name' field is not updated in student_info.json.")
            return 0, feedback
        elif not sid or "YOUR STUDENT ID" in sid.upper():
            feedback.append("FAIL: 'student_id' field is not updated in student_info.json.")
            return 0, feedback
        elif not gh_user or "YOUR GITHUB USERNAME" in gh_user.upper():
            feedback.append("FAIL: 'github_username' field is not updated in student_info.json.")
            return 0, feedback
        else:
            score += 10
            feedback.append(f"PASS: student_info.json valid ({name}, {sid}, @{gh_user}).")
    except Exception as e:
        feedback.append(f"FAIL: Error parsing student_info.json: {str(e)}")
        return 0, feedback

    stdout, _, code = run_cmd('git log -1 --format="%an <%ae>"')
    if code == 0 and stdout and "@" in stdout:
        score += 5
        feedback.append(f"PASS: Git commit author configured: {stdout}")
    else:
        feedback.append("WARN: Git commit author email not verified in recent commit history.")
        
    return score, feedback


def check_task_2():
    """Task 2: .gitignore file configuration (15 pts)."""
    score = 0
    feedback = []
    
    gitignore_path = ".gitignore"
    if not os.path.exists(gitignore_path):
        return 0, ["FAIL: .gitignore file does not exist."]
        
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    required_patterns = ["*.log", "temp/", "lectures/"]
    found_patterns = []
    
    for pattern in required_patterns:
        clean_pat = pattern.rstrip('/')
        if clean_pat in content:
            found_patterns.append(pattern)
            
    if len(found_patterns) >= 2:
        score += 10
        feedback.append(f"PASS: .gitignore contains required ignore patterns: {', '.join(found_patterns)}")
        
        stdout, _, _ = run_cmd("git ls-files")
        tracked_files = stdout.splitlines()
        log_files_tracked = [f for f in tracked_files if f.endswith(".log") or f.startswith("temp/")]
        
        if len(log_files_tracked) == 0:
            score += 5
            feedback.append("PASS: No temporary or log files are tracked in Git.")
        else:
            feedback.append(f"FAIL: Prohibited files tracked in Git: {log_files_tracked}")
    else:
        feedback.append("FAIL: .gitignore missing rules for *.log, temp/, or lectures/.")
        
    return score, feedback


def check_task_3():
    """Task 3: Branching & calculator.py implementation (20 pts)."""
    score = 0
    feedback = []
    
    stdout_br, _, _ = run_cmd("git branch -a")
    stdout_log, _, _ = run_cmd("git log --oneline")
    has_calc_branch = "feature/calculator" in stdout_br or "feature-calculator" in stdout_br or "calculator" in stdout_log.lower()
    if has_calc_branch:
        score += 5
        feedback.append("PASS: Feature branch 'feature/calculator' detected.")
    else:
        feedback.append("WARN: Branch 'feature/calculator' not found in local/remote branches.")
        
    calc_path = os.path.join("src", "calculator.py")
    if not os.path.exists(calc_path):
        return score, feedback + ["FAIL: src/calculator.py file missing."]
        
    try:
        spec = importlib.util.spec_from_file_location("calculator", calc_path)
        calc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(calc)
        
        if hasattr(calc, 'add') and hasattr(calc, 'multiply'):
            res_add = calc.add(10, 5)
            res_mul = calc.multiply(4, 3)
            
            if res_add == 15 and res_mul == 12:
                score += 15
                feedback.append("PASS: calculator.py functions add() and multiply() work correctly.")
            else:
                feedback.append(f"FAIL: Function output mismatch: add(10,5)={res_add} (expected 15), multiply(4,3)={res_mul} (expected 12).")
        else:
            feedback.append("FAIL: add() or multiply() function missing in src/calculator.py.")
    except Exception as e:
        feedback.append(f"FAIL: Error importing src/calculator.py: {str(e)}")
        
    return score, feedback


def check_task_4():
    """Task 4: Merge conflict resolution in src/app.py (20 pts)."""
    score = 0
    feedback = []
    
    app_path = os.path.join("src", "app.py")
    if not os.path.exists(app_path):
        return 0, ["FAIL: src/app.py does not exist."]
        
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    conflict_markers = ["<<<<<<<", "=======", ">>>>>>>"]
    has_conflict_markers = any(marker in content for marker in conflict_markers)
    
    if has_conflict_markers:
        feedback.append("FAIL: src/app.py contains unresolved merge conflict markers (<<<<<<<, =======, >>>>>>>).")
        return 0, feedback

    stdout_branches, _, _ = run_cmd("git branch -a")
    stdout_log, _, _ = run_cmd("git log --oneline")

    has_branch = "feature/conflict-fix" in stdout_branches or "feature/conflict-fix" in stdout_log
    has_merge_commit = "resolve merge conflict" in stdout_log.lower() or "merge" in stdout_log.lower() or "conflict" in stdout_log.lower()

    if has_branch or has_merge_commit:
        score += 5
        feedback.append("PASS: Branch 'feature/conflict-fix' detected.")
    else:
        feedback.append("FAIL: Branch 'feature/conflict-fix' not found.")

    if has_merge_commit:
        score += 5
        feedback.append("PASS: Conflict resolution commit found in git log.")
    else:
        feedback.append("FAIL: Merge conflict resolution commit not found in git log.")

    if not has_conflict_markers and (has_branch or has_merge_commit):
        try:
            spec = importlib.util.spec_from_file_location("app", app_path)
            app = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(app)
            
            if hasattr(app, 'greet'):
                output = app.greet("Alice")
                if isinstance(output, str) and len(output) > 0:
                    score += 10
                    feedback.append(f"PASS: app.py executes cleanly and greet() returned: '{output}'.")
                else:
                    feedback.append("FAIL: greet() did not return a valid string.")
            else:
                feedback.append("FAIL: greet() function missing in src/app.py.")
        except Exception as e:
            feedback.append(f"FAIL: Error running src/app.py: {str(e)}")
    else:
        feedback.append("FAIL: app.py execution test skipped until branch and merge conflict resolution are completed.")
        
    return score, feedback


def check_task_5():
    """Task 5: Git Stashing & Tagging v1.0.0 (15 pts)."""
    score = 0
    feedback = []
    
    notes_path = os.path.join("src", "notes.txt")
    if os.path.exists(notes_path):
        with open(notes_path, 'r', encoding='utf-8') as f:
            notes_content = f.read()
        if "[x]" in notes_content.lower():
            score += 7
            feedback.append("PASS: Stashed changes applied to src/notes.txt (checklist checked).")
        else:
            feedback.append("FAIL: src/notes.txt checklist items are unchecked [ ].")
    else:
        feedback.append("FAIL: src/notes.txt missing.")

    stdout, _, _ = run_cmd("git tag -l")
    tags = stdout.splitlines()
    if "v1.0.0" in tags:
        score += 8
        feedback.append("PASS: Git release tag 'v1.0.0' successfully created.")
    else:
        feedback.append("FAIL: Git release tag 'v1.0.0' not found (create with: git tag -a v1.0.0 -m 'Release v1.0.0').")

    return score, feedback


def check_task_6():
    """Task 6: GitHub Reflection document completion (15 pts)."""
    score = 0
    feedback = []
    
    refl_path = "GITHUB_REFLECTION.md"
    if not os.path.exists(refl_path):
        return 0, ["FAIL: GITHUB_REFLECTION.md file missing."]
        
    with open(refl_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    placeholder = "[Write your response here"
    placeholders_remaining = content.count(placeholder)
    
    if placeholders_remaining == 0 and len(content.strip()) > 300:
        score += 15
        feedback.append("PASS: GITHUB_REFLECTION.md completed with detailed answers.")
    elif placeholders_remaining < 3:
        score += 8
        feedback.append("WARN: GITHUB_REFLECTION.md partially completed.")
    else:
        feedback.append("FAIL: GITHUB_REFLECTION.md contains unedited placeholder text.")
        
    return score, feedback


def main():
    print(f"{Colors.BOLD}{Colors.BLUE}=================================================={Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}   Git & GitHub Practice Assignment Autograder   {Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}=================================================={Colors.RESET}\n")
    
    task_checkers = {
        1: ("Task 1: Git Config & Student Info (15 pts)", check_task_1),
        2: ("Task 2: .gitignore Rules (15 pts)", check_task_2),
        3: ("Task 3: Branching & Calculator (20 pts)", check_task_3),
        4: ("Task 4: Merge Conflict Resolution (20 pts)", check_task_4),
        5: ("Task 5: Git Stashing & Tagging (15 pts)", check_task_5),
        6: ("Task 6: GitHub Reflection (15 pts)", check_task_6),
    }

    target_task = None
    if len(sys.argv) > 2 and sys.argv[1] == "--task":
        try:
            target_task = int(sys.argv[2])
        except ValueError:
            pass

    total_score = 0
    max_possible = 0

    results_summary = []
    for num, (title, checker) in task_checkers.items():
        if target_task is not None and num != target_task:
            continue

        max_pts = TASK_WEIGHTS[num]
        max_possible += max_pts
        score, feedback = checker()
        total_score += score
        results_summary.append((title, score, max_pts, feedback))
        
        status_color = Colors.GREEN if score == max_pts else (Colors.YELLOW if score > 0 else Colors.RED)
        print(f"{Colors.BOLD}{title}{Colors.RESET}")
        print(f"  Score: {status_color}{score}/{max_pts} pts{Colors.RESET}")
        for item in feedback:
            print(f"  └─ {item}")
        print()

    print(f"{Colors.BOLD}--------------------------------------------------{Colors.RESET}")
    final_color = Colors.GREEN if total_score == max_possible else Colors.YELLOW
    print(f"{Colors.BOLD}TOTAL SCORE: {final_color}{total_score} / {max_possible} pts{Colors.RESET}")
    print(f"{Colors.BOLD}--------------------------------------------------{Colors.RESET}\n")

    summary_file = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_file:
        try:
            with open(summary_file, "a", encoding="utf-8") as f:
                f.write("### 📊 Git & GitHub Practice Assignment — Grade Summary\n\n")
                f.write("| Task | Status | Score | Feedback |\n")
                f.write("| :--- | :---: | :---: | :--- |\n")
                for title, score, max_pts, feedback in results_summary:
                    status = "✅ PASS" if score == max_pts else ("⚠️ PARTIAL" if score > 0 else "❌ FAIL")
                    fb_str = "<br>".join(feedback)
                    f.write(f"| **{title}** | {status} | **{score} / {max_pts} pts** | {fb_str} |\n")
                
                final_status = "✅ PASS" if total_score == max_possible else "⚠️ INCOMPLETE"
                pct = int((total_score / max_possible) * 100) if max_possible > 0 else 0
                f.write(f"| **TOTAL SCORE** | **{final_status}** | **{total_score} / {max_possible} pts** | **Grade: {pct}%** |\n\n")
        except Exception:
            pass

    if total_score < max_possible:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
