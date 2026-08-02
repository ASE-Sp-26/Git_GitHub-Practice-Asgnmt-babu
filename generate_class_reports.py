#!/usr/bin/env python3
"""
Master Class Report & Individual Student PDF Generator
Course: Advanced Software Engineering (ASE)

Generates:
1. Moodle-Compatible Consolidated Gradebook: moodle_consolidated_grades.csv
2. Individual Student Evaluation Reports: evaluation_reports/<StudentID>_<StudentName>_Evaluation.pdf

Usage:
    python generate_class_reports.py [--dir ./Student-testing]
"""

import os
import sys
import json
import csv
import re
import datetime
import importlib.util

class RobustPDFWriter:
    """Zero-dependency, pure-Python valid PDF 1.4 Document Generator."""
    def __init__(self, filename):
        self.filename = filename

    def build_student_pdf(self, name, sid, gh_user, task_data, total_score, max_possible):
        pct = int((total_score / max_possible) * 100) if max_possible > 0 else 0
        status_str = "PASSED" if total_score == max_possible else ("PARTIAL" if total_score > 0 else "FAILED")
        date_str = datetime.datetime.now().strftime("%B %d, %Y")

        stream_cmds = []
        
        stream_cmds.append("0.1 0.2 0.4 rg 40 730 532 45 re f")
        stream_cmds.append("BT /F1 16 Tf 1 1 1 rg 55 754 Td (Advanced Software Engineering - Evaluation Report) Tj ET")
        stream_cmds.append("BT /F2 9 Tf 0.9 0.9 0.9 rg 55 738 Td (Course Code: ASE-Sp26 | Assignment: Git & GitHub Practice) Tj ET")

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

        stream_cmds.append("BT /F1 12 Tf 0 0 0 rg 40 550 Td (Task Breakdown & Feedback:) Tj ET")
        
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


def main():
    target_dir = "."
    if len(sys.argv) > 2 and sys.argv[1] == "--dir":
        target_dir = sys.argv[2]

    moodle_file = "moodle_consolidated_grades.csv"
    pdf_dir = "evaluation_reports"
    os.makedirs(pdf_dir, exist_ok=True)

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

    repo_dirs = []
    if os.path.exists(target_dir):
        for root, dirs, files in os.walk(target_dir):
            if "student_info.json" in files and "autograder.py" in files:
                repo_dirs.append(root)

    if not repo_dirs:
        print(f"Directory '{target_dir}' contains no student folders. Use fetch_class_moodle_report.py to fetch API grades.")
        return

    print(f"==================================================")
    print(f"  ASE Master Class Report & PDF Evaluation Suite  ")
    print(f"==================================================\n")
    print(f"Processing {len(repo_dirs)} student repository folder(s)...\n")

    for repo_path in repo_dirs:
        info_path = os.path.join(repo_path, "student_info.json")
        
        name = "Unknown Student"
        sid = "UNKNOWN-ID"
        gh_user = "unknown"
        
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                name = str(data.get("full_name", name)).strip()
                sid = str(data.get("student_id", sid)).strip()
                gh_user = str(data.get("github_username", gh_user)).strip()
        except Exception:
            pass

        # Exclude template placeholders
        if name == "YOUR NAME HERE" or sid == "YOUR STUDENT ID HERE":
            continue

        old_cwd = os.getcwd()
        os.chdir(repo_path)
        
        mod = load_autograder_module(".")
        
        task_details = []
        task_scores = {}
        total_score = 0
        max_possible = 100

        checkers = {
            1: ("Task 1: Git Config & Student Info", getattr(mod, "check_task_1", None), 15),
            2: ("Task 2: .gitignore Configuration", getattr(mod, "check_task_2", None), 15),
            3: ("Task 3: Branching & Calculator", getattr(mod, "check_task_3", None), 20),
            4: ("Task 4: Merge Conflict Resolution", getattr(mod, "check_task_4", None), 20),
            5: ("Task 5: Git Stashing & Tagging", getattr(mod, "check_task_5", None), 15),
            6: ("Task 6: GitHub Reflection", getattr(mod, "check_task_6", None), 15),
        }

        for num, (title, func, max_pts) in checkers.items():
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
            total_score += score
            task_details.append((title, score, max_pts, feedback))

        os.chdir(old_cwd)

        pct = f"{int((total_score / max_possible) * 100)}%"
        status = "PASSED" if total_score == max_possible else ("PARTIAL" if total_score > 0 else "FAILED")

        moodle_records.append([
            sid,
            name,
            gh_user,
            task_scores.get(1, 0),
            task_scores.get(2, 0),
            task_scores.get(3, 0),
            task_scores.get(4, 0),
            task_scores.get(5, 0),
            task_scores.get(6, 0),
            total_score,
            pct,
            status
        ])

        clean_sid = "".join(c for c in sid if c.isalnum() or c in ['-', '_'])
        clean_name = "".join(c for c in name if c.isalnum() or c == '_').replace(' ', '_')
        pdf_filename = os.path.join(pdf_dir, f"{clean_sid}_{clean_name}_Evaluation.pdf")
        
        pdf_writer = RobustPDFWriter(pdf_filename)
        pdf_writer.build_student_pdf(name, sid, gh_user, task_details, total_score, max_possible)
        
        print(f"  ✔ Student: {name:20s} ({sid:15s}) | Score: {total_score:3d}/100 pts | PDF: {os.path.basename(pdf_filename)}")

    with open(moodle_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(moodle_headers)
        writer.writerows(moodle_records)

    print(f"\n==================================================")
    print(f"  OUTPUTS GENERATED SUCCESSFULLY  ")
    print(f"==================================================")
    print(f"1. Moodle Gradebook CSV : {os.path.abspath(moodle_file)}")
    print(f"2. Individual Student PDFs: {os.path.abspath(pdf_dir)}/")
    print(f"==================================================\n")

if __name__ == "__main__":
    main()
