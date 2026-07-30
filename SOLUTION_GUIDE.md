# Git & GitHub Practice Assignment: Instructor Solution Guide

This document is an instructor reference detailing the exact terminal commands and file edits required to achieve a **100/100 score** on the assignment.

---

## Task-by-Task Solution Walkthrough

### Task 1 Solution: Student Information & Git Config
1. Edit `student_info.json`:
   ```json
   {
     "full_name": "Instructor Validation",
     "student_id": "INS-2026-001",
     "github_username": "instructor-ase"
   }
   ```
2. Configure Git user:
   ```bash
   git config user.name "Instructor Validation"
   git config user.email "instructor@nust.edu.pk"
   ```
3. Commit change:
   ```bash
   git add student_info.json
   git commit -m "docs: update student info"
   ```

---

### Task 2 Solution: `.gitignore` Configuration
1. Open `.gitignore` and append:
   ```gitignore
   *.log
   temp/
   lectures/
   ```
2. Commit change:
   ```bash
   git add .gitignore
   git commit -m "chore: update .gitignore rules"
   ```

---

### Task 3 Solution: Branching & Feature Development
1. Create and switch to branch:
   ```bash
   git checkout -b feature/calculator
   ```
2. Update `src/calculator.py`:
   ```python
   def add(a, b):
       return a + b

   def multiply(a, b):
       return a * b
   ```
3. Commit and merge:
   ```bash
   git add src/calculator.py
   git commit -m "feat: implement calculator functions"
   git checkout main
   git merge feature/calculator
   ```

---

### Task 4 Solution: Merge Conflict Resolution
1. Create conflict branch `feature/conflict-fix` and edit `src/app.py`:
   ```bash
   git checkout -b feature/conflict-fix
   ```
   In `src/app.py`:
   ```python
   def greet(name):
       return f"Hi {name}, welcome to the Git & GitHub Practice Assignment!"
   ```
   Commit:
   ```bash
   git add src/app.py
   git commit -m "style: update greeting on conflict-fix branch"
   ```
2. Return to `main` and edit `src/app.py` differently:
   ```bash
   git checkout main
   ```
   In `src/app.py`:
   ```python
   def greet(name):
       return f"Hello, {name}! Welcome to Advanced Software Engineering (ASE)."
   ```
   Commit:
   ```bash
   git add src/app.py
   git commit -m "style: update main greeting"
   ```
3. Merge `feature/conflict-fix` into `main` to produce conflict:
   ```bash
   git merge feature/conflict-fix
   ```
4. Resolve conflict in `src/app.py` by choosing clean code without `<<<<<<<` markers:
   ```python
   def greet(name):
       return f"Hello, {name}! Welcome to ASE Git Practice."
   ```
5. Commit merge:
   ```bash
   git add src/app.py
   git commit -m "fix: resolve merge conflict in app.py"
   ```

---

### Task 5 Solution: Git Stashing & Tagging
1. Update `src/notes.txt` to mark all checklist items checked `[x]`.
2. Apply stash / commit:
   ```bash
   git add src/notes.txt
   git commit -m "docs: complete assignment release checklist"
   ```
3. Create annotated tag `v1.0.0`:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   ```

---

### Task 6 Solution: GitHub Reflection Document
1. Edit `GITHUB_REFLECTION.md` to answer all 3 questions thoughtfully:
   - **Q1**: `git fetch` downloads commits, files, and refs from a remote repository without merging them into your local branch. In contrast, `git pull` executes `git fetch` followed immediately by `git merge` to integrate remote changes into your active branch.
   - **Q2**: A Pull Request (PR) notifies team members that a feature branch is ready for review. Code reviews allow peers to catch bugs, ensure architectural quality, and maintain consistent coding standards before code is merged to main.
   - **Q3**: Feature branching isolates work so multiple developers can work on distinct features simultaneously without overwriting each other's code or destabilizing the main production branch.
2. Commit:
   ```bash
   git add GITHUB_REFLECTION.md
   git commit -m "docs: complete reflection questions"
   ```
