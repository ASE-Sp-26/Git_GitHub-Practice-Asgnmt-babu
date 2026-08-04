# Git & GitHub Practice Assignment

Welcome to the **Git & GitHub Practice Assignment** repository!

This repository contains practical exercises designed to test your knowledge of basic Git commands, advanced Git workflows (branching, merge conflicts, stashing, tagging), and GitHub collaboration best practices using Pull Requests.

---

## 📚 Reference Manuals & Documents

Before starting your work, please review the following guide files included in this repository:
- 📖 [**`ASSIGNMENT_INSTRUCTIONS.md`**](ASSIGNMENT_INSTRUCTIONS.md): Comprehensive step-by-step narrative guide for completing all tasks.
- 📊 [**`RUBRIC.md`**](RUBRIC.md): Detailed grading rubric matrix and point breakdown.

---

## ⚡ Task & Point Summary (100 Points Total)

| Task # | Task Title | Lecture Mapped | Points | Key Commands / Files |
|---|---|---|---|---|
| **Task 1** | Git Config & Student Info | Lec 4 (Basic Git) | 15 pts | `student_info.json`, `git config` |
| **Task 2** | `.gitignore` File Rules | Lec 4 (Config Mgmt) | 15 pts | `.gitignore` |
| **Task 3** | Branching & Feature Dev | Lec 5 (Advanced Git) | 20 pts | `git checkout -b feature/calculator`, `src/calculator.py` |
| **Task 4** | Merge Conflict Resolution | Lec 5 (Advanced Git) | 20 pts | `git merge feature/conflict-fix`, `src/app.py` |
| **Task 5** | Git Stashing & Tagging | Lec 5 (Advanced Git) | 15 pts | `git stash apply`, `git tag -a v1.0.0`, `src/notes.txt` |
| **Task 6** | GitHub PR & Reflection | Lec 6 (GitHub & PRs) | 15 pts | `GITHUB_REFLECTION.md` |

---

## 🚀 Submission Workflow & Autograding

1. **Fork this repository** to your personal GitHub account.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/<your-github-username>/Git_GitHub-Practice-Asgnmt.git
   cd Git_GitHub-Practice-Asgnmt
   ```
3. Complete Tasks 1–6 and test your work locally anytime:
   ```bash
   python autograder.py
   ```
4. Push all commits, branches, and tags to your fork on GitHub:
   ```bash
   git push origin main --all --tags
   ```
5. **Open a Pull Request (PR)** from your fork's `main` branch to the instructor repository (`ClassroomAsignments/Git_GitHub-Practice-Asgnmt:main`).
6. GitHub Actions will automatically grade your PR and post your itemized score directly as a PR comment!

