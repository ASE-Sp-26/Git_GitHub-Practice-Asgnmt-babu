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
import subprocess
import datetime

class SimplePDFWriter:
    """Zero-dependency, pure-Python PDF 1.4 Document Generator."""
    def __init__(self, filename):
        self.filename = filename
        self.objects = []
        self.offsets = []
        self.stream = bytearray()
        
    def _add_object(self, content):
        offset = len(self.stream)
        self.offsets.append(offset)
        obj_id = len(self.offsets)
        obj_str = f"{obj_id} 0 obj\n{content}\nendobj\n"
        self.stream.extend(obj_str.encode('utf-8'))
        return obj_id

    def build_student_pdf(self, name, sid, gh_user, task_data, total_score, max_possible):
        # Reset stream
        self.stream = bytearray()
        self.offsets = []
        self.stream.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        pct = int((total_score / max_possible) * 100) if max_possible > 0 else 0
        status_str = "PASSED" if total_score == max_possible else ("PARTIAL" if total_score > 0 else "FAILED")
        date_str = datetime.datetime.now().strftime("%B %d, %Y")

        # Build Page Content Stream
        text_ops = []
        
        # Header Title
        text_ops.append("BT /F1 18 Tf 50 750 Td (Advanced Software Engineering - Student Evaluation Report) Tj ET")
        text_ops.append("BT /F2 10 Tf 50 735 Td (Course Code: ASE-Sp26 | Topic: Git & GitHub Practice Assignment) Tj ET")
        
        # Divider line 1
        text_ops.append("0.7 0.7 0.7 RG 1 w 50 725 m 550 725 l S")

        # Student Information Box
        text_ops.append("0.95 0.95 0.98 rg 50 645 500 70 re f")
        text_ops.append("0.8 0.8 0.85 RG 1 w 50 645 500 70 re s")
        
        text_ops.append(f"BT /F1 11 Tf 65 698 Td (Student Name:) Tj ET")
        text_ops.append(f"BT /F2 11 Tf 165 698 Td ({self._escape(name)}) Tj ET")
        text_ops.append(f"BT /F1 11 Tf 320 698 Td (Student ID:) Tj ET")
        text_ops.append(f"BT /F2 11 Tf 410 698 Td ({self._escape(sid)}) Tj ET")

        text_ops.append(f"BT /F1 11 Tf 65 675 Td (GitHub Username:) Tj ET")
        text_ops.append(f"BT /F2 11 Tf 165 675 Td (@{self._escape(gh_user)}) Tj ET")
        text_ops.append(f"BT /F1 11 Tf 320 675 Td (Date Evaluated:) Tj ET")
        text_ops.append(f"BT /F2 11 Tf 410 675 Td ({date_str}) Tj ET")

        # Grade Scorecard Box
        if status_str == "PASSED":
            text_ops.append("0.90 0.97 0.90 rg 50 575 500 55 re f")
            text_ops.append("0.3 0.7 0.3 RG 1.5 w 50 575 500 55 re s")
            score_color = "0.1 0.5 0.1 rg"
        else:
            text_ops.append("0.98 0.92 0.92 rg 50 575 500 55 re f")
            text_ops.append("0.8 0.3 0.3 RG 1.5 w 50 575 500 55 re s")
            score_color = "0.7 0.1 0.1 rg"

        text_ops.append(f"BT /F1 14 Tf 65 608 Td (FINAL GRADE:) Tj ET")
        text_ops.append(f"BT /F1 16 Tf 170 608 Td ({total_score} / {max_possible} Points  \({pct}%\)) Tj ET")
        text_ops.append(f"BT /F1 14 Tf 420 608 Td (STATUS: {status_str}) Tj ET")

        # Task Breakdown Header
        text_ops.append("BT /F1 13 Tf 50 545 Td (Task Breakdown & Autograder Feedback:) Tj ET")
        
        # Table Header Box
        text_ops.append("0.2 0.3 0.5 rg 50 515 500 22 re f")
        text_ops.append("BT /F1 10 Tf 60 522 Td (Task Name) Tj ET")
        text_ops.append("BT /F1 10 Tf 330 522 Td (Score) Tj ET")
        text_ops.append("BT /F1 10 Tf 430 522 Td (Status) Tj ET")

        y = 485
        for t_title, score, max_pts, feedback in task_data:
            t_status = "PASS" if score == max_pts else ("PARTIAL" if score > 0 else "FAIL")
            
            # Row background
            text_ops.append(f"0.97 0.97 0.97 rg 50 {y-5} 500 25 re f")
            text_ops.append(f"0.85 0.85 0.85 RG 0.5 w 50 {y-5} 500 25 re s")

            text_ops.append(f"BT /F1 9 Tf 60 {y+5} Td ({self._escape(t_title)}) Tj ET")
            text_ops.append(f"BT /F2 9 Tf 335 {y+5} Td ({score}/{max_pts} pts) Tj ET")
            text_ops.append(f"BT /F1 9 Tf 435 {y+5} Td ({t_status}) Tj ET")
            
            # Feedback lines
            fb_y = y - 18
            for fb_item in feedback[:2]: # Show top 2 feedback lines
                text_ops.append(f"BT /F2 8 Tf 70 {fb_y} Td (- {self._escape(fb_item)}) Tj ET")
                fb_y -= 12
            
            y -= 45

        # Footer
        text_ops.append("0.7 0.7 0.7 RG 1 w 50 50 m 550 50 l S")
        text_ops.append("BT /F2 8 Tf 50 35 Td (Generated automatically by ASE Autograder System. Official Record.) Tj ET")

        content_stream = "\n".join(text_ops)
        content_bytes = content_stream.encode('utf-8')

        # Add Objects
        # Obj 1: Catalog
        # Obj 2: Pages
        # Obj 3: Page
        # Obj 4: Content Stream
        # Obj 5: Font F1 (Helvetica-Bold)
        # Obj 6: Font F2 (Helvetica)

        content_obj_id = self._add_object(f"<</Length {len(content_bytes)}>>\nstream\n{content_stream}\nendstream")
        font1_obj_id = self._add_object("<</Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold>>")
        font2_obj_id = self._add_object("<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>")
        
        resources_obj_id = self._add_object(f"<</Font <</F1 {font1_obj_id} 0 R /F2 {font2_obj_id} 0 R>>>>")
        page_obj_id = self._add_object(f"<</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {content_obj_id} 0 R /Resources {resources_obj_id} 0 R>>")
        pages_obj_id = self._add_object(f"<</Type /Pages /Kids [{page_obj_id} 0 R] /Count 1>>")
        catalog_obj_id = self._add_object(f"<</Type /Catalog /Pages {pages_obj_id} 0 R>>")

        # Xref Table
        xref_offset = len(self.stream)
        self.stream.extend(f"xref\n0 {len(self.offsets) + 1}\n0000000000 65535 f \n".encode('utf-8'))
        for off in self.offsets:
            self.stream.extend(f"{off:010d} 00000 n \n".encode('utf-8'))

        # Trailer
        trailer_str = f"trailer\n<</Size {len(self.offsets) + 1} /Root {catalog_obj_id} 0 R>>\nstartxref\n{xref_offset}\n%%EOF\n"
        self.stream.extend(trailer_str.encode('utf-8'))

        # Write to disk
        with open(self.filename, 'wb') as f:
            f.write(self.stream)

    def _escape(self, text):
        return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def main():
    target_dir = "Student-testing"
    if len(sys.argv) > 2 and sys.argv[1] == "--dir":
        target_dir = sys.argv[2]
        
    if not os.path.exists(target_dir):
        print(f"Directory '{target_dir}' not found. Scanning current directory for student repos...")
        target_dir = "."

    moodle_file = "moodle_consolidated_grades.csv"
    pdf_dir = "evaluation_reports"
    os.makedirs(pdf_dir, exist_ok=True)

    # Moodle Gradebook Standard Header Format
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

    # Find student repository folders
    repo_dirs = []
    for root, dirs, files in os.walk(target_dir):
        if "student_info.json" in files and "autograder.py" in files:
            repo_dirs.append(root)

    if not repo_dirs:
        print("No student repositories found with student_info.json and autograder.py.")
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
                name = data.get("full_name", name).strip()
                sid = data.get("student_id", sid).strip()
                gh_user = data.get("github_username", gh_user).strip()
        except Exception:
            pass

        # Evaluate each task using autograder.py --task N
        task_details = []
        total_score = 0
        max_possible = 100
        
        task_scores = {}
        for task_num in range(1, 7):
            try:
                res = subprocess.run(
                    f"python autograder.py --task {task_num}",
                    shell=True,
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                
                score = 0
                feedback_lines = []
                for line in res.stdout.splitlines():
                    if "Score:" in line and "pts" in line:
                        parts = line.split("Score:")[-1].strip().split("/")[0]
                        score = int(''.join(filter(str.isdigit, parts)))
                    elif "└─" in line:
                        feedback_lines.append(line.replace("└─", "").strip())
                
                max_pts = 15 if task_num in [1, 2, 5, 6] else 20
                task_title = f"Task {task_num}"
                task_details.append((task_title, score, max_pts, feedback_lines))
                task_scores[task_num] = score
                total_score += score
            except Exception:
                task_scores[task_num] = 0
                task_details.append((f"Task {task_num}", 0, 15, ["FAIL: Execution error."]))

        pct = f"{int((total_score / max_possible) * 100)}%"
        status = "PASSED" if total_score == max_possible else ("PARTIAL" if total_score > 0 else "FAILED")

        # 1. Build Moodle Record
        moodle_records.append([
            sid,            # Primary Identifier for Moodle
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

        # 2. Build Individual Student PDF Evaluation Sheet
        clean_sid = "".join(c for c in sid if c.isalnum() or c in ['-', '_'])
        clean_name = "".join(c for c in name if c.isalnum() or c == '_').replace(' ', '_')
        pdf_filename = os.path.join(pdf_dir, f"{clean_sid}_{clean_name}_Evaluation.pdf")
        
        pdf_writer = SimplePDFWriter(pdf_filename)
        pdf_writer.build_student_pdf(name, sid, gh_user, task_details, total_score, max_possible)
        
        print(f"  ✔ Student: {name:20s} ({sid:15s}) | Score: {total_score:3d}/100 pts | PDF: {os.path.basename(pdf_filename)}")

    # Write Moodle CSV File
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
