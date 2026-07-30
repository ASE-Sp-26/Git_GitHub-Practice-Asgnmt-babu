# Git & GitHub Practice Assignment

Welcome to the **Git & GitHub Practice Assignment** template repository for GitHub Classroom!

This repository contains practical exercises designed to test your knowledge of basic Git commands, advanced Git workflows (branching, merge conflicts, stashing, tagging), and GitHub collaboration best practices.

---

## 📚 Reference Manuals & Documents

Before starting your work, please review the following guide files included in this repository:
- 📖 [**`ASSIGNMENT_INSTRUCTIONS.md`**](ASSIGNMENT_INSTRUCTIONS.md): Comprehensive step-by-step narrative guide for completing all tasks.
- 📊 [**`RUBRIC.md`**](RUBRIC.md): Detailed grading rubric matrix and point breakdown.
- 💡 [**`SOLUTION_GUIDE.md`**](SOLUTION_GUIDE.md): Instructor reference solution walkthrough.

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

## 🧪 Local Testing & Autograding

You can test your progress locally at any time on Windows, macOS, or Linux without extra dependencies:

```bash
python autograder.py
```

When you push your commits to GitHub (`git push origin main --tags`), GitHub Actions will automatically evaluate your work and report your final grade directly to GitHub Classroom!
