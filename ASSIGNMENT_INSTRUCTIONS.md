# Git & GitHub Practice Assignment: Student Handbook

**Course:** Advanced Software Engineering (ASE)  
**Topic:** Version Control System (VCS), Advanced Git Operations, and GitHub Collaboration  
**Lectures Covered:** Lecture 4 (Config Mgmt & Git), Lecture 5 (Advanced Git), Lecture 6 (GitHub)  
**Time Required:** 2-3 Hours  
**Total Points:** 100 Points  

---

## 🎯 Learning Objectives

By completing this assignment, you will gain hands-on proficiency in:
1. Configuring Git identity and maintaining accurate commit metadata.
2. Managing workspace state and clean repositories with `.gitignore` patterns.
3. Feature branching workflows (`git branch`, `git checkout`, conventional commit messages).
4. Identifying, understanding, and resolving Git merge conflicts.
5. Preserving uncommitted progress with Git stashing (`git stash`) and tagging software releases (`git tag`).
6. GitHub collaboration workflows, Pull Requests (PRs), remote operations, and code reviews.

---

## 🚀 Quick Setup & Execution

### Step 1: Fork and Clone your Assignment Repository
1. **Fork this repository** (`https://github.com/ClassroomAsignments/Git_GitHub-Practice-Asgnmt`) to your personal GitHub account using the "Fork" button on GitHub.
2. Clone your fork locally using:
```bash
git clone https://github.com/<your-github-username>/Git_GitHub-Practice-Asgnmt.git
cd Git_GitHub-Practice-Asgnmt
```

### Step 2: Test your progress locally anytime!
You do **NOT** need to wait for GitHub CI to test your work. You can check your score locally at any moment by running:
```bash
python autograder.py
```
To run autograding for a single task (e.g., Task 3):
```bash
python autograder.py --task 3
```

---

## 📋 Task Walkthrough & Instructions

### Task 1: Git Configuration & Student Details (15 Points)
*Lecture Mapped: Lecture 4 - Basic Git & Configuration*

1. Open `student_info.json` in your code editor.
2. Replace the placeholder values with your actual Name, Student ID, and GitHub Username:
   ```json
   {
     "full_name": "Jane Doe",
     "student_id": "2026-ASE-042",
     "github_username": "janedoe-ase"
   }
   ```
3. Ensure your local Git identity is configured with your name and email:
   ```bash
   git config user.name "Jane Doe"
   git config user.email "janedoe@example.com"
   ```
4. Commit your changes:
   ```bash
   git add student_info.json
   git commit -m "docs: update student_info.json with student credentials"
   ```

---

### Task 2: Managing Repository State with `.gitignore` (15 Points)
*Lecture Mapped: Lecture 4 - Configuration Management & File States*

1. Open `.gitignore` in the repository root directory.
2. Add rules to ignore temporary files, log files, lecture materials, and build artifacts:
   ```gitignore
   *.log
   temp/
   lectures/
   __pycache__/
   *.pyc
   ```
3. Test your `.gitignore` rules locally by ensuring temporary files are not tracked:
   ```bash
   git status
   ```
4. Commit your `.gitignore` updates:
   ```bash
   git add .gitignore
   git commit -m "chore: update .gitignore rules for logs and build artifacts"
   ```

---

### Task 3: Branching & Feature Development (20 Points)
*Lecture Mapped: Lecture 5 - Advanced Git (Branching & Switching)*

1. Create and switch to a new feature branch named `feature/calculator`:
   ```bash
   git checkout -b feature/calculator
   ```
2. Open `src/calculator.py` and implement the `add(a, b)` and `multiply(a, b)` functions:
   ```python
   def add(a, b):
       return a + b

   def multiply(a, b):
       return a * b
   ```
3. Stage and commit your changes on the `feature/calculator` branch:
   ```bash
   git add src/calculator.py
   git commit -m "feat: implement add and multiply functions in calculator.py"
   ```
4. Switch back to the `main` branch:
   ```bash
   git checkout main
   ```
5. Merge your feature branch into `main`:
   ```bash
   git merge feature/calculator
   ```

---

### Task 4: Resolving Merge Conflicts (20 Points)
*Lecture Mapped: Lecture 5 - Advanced Git (Merge Conflicts)*

1. Create a branch named `feature/conflict-fix` (if not already existing):
   ```bash
   git checkout -b feature/conflict-fix
   ```
2. Modify `src/app.py` on this branch to return a new greeting string, then commit:
   ```bash
   git add src/app.py
   git commit -m "style: update app greeting on conflict branch"
   ```
3. Switch back to `main`:
   ```bash
   git checkout main
   ```
4. Modify line 5 of `src/app.py` on `main` to a different string and commit on `main`.
5. Now, attempt to merge `feature/conflict-fix` into `main`:
   ```bash
   git merge feature/conflict-fix
   ```
6. Git will flag a **MERGE CONFLICT** in `src/app.py`.
7. Open `src/app.py` in your code editor. You will see conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
8. Edit `src/app.py` to remove **all** conflict markers, combine the desired code cleanly, save the file, and complete the merge commit:
   ```bash
   git add src/app.py
   git commit -m "fix: resolve merge conflict in src/app.py"
   ```

---

### Task 5: Git Stashing & Tagging Releases (15 Points)
*Lecture Mapped: Lecture 5 - Advanced Git (Stashing & Tagging)*

1. Suppose you started edits on `src/notes.txt` but had to stash them.
2. Edit `src/notes.txt` to mark all checklist items as completed `[x]`:
   ```text
   [x] Task 1: Student info added
   [x] Task 2: Gitignore updated
   [x] Task 3: Calculator implemented
   [x] Task 4: Merge conflict resolved
   [x] Task 5: Stash applied and release tagged v1.0.0
   [x] Task 6: GitHub reflection completed
   ```
3. Stash your changes:
   ```bash
   git stash
   ```
4. Apply your stashed changes back:
   ```bash
   git stash apply
   ```
5. Commit the updated `src/notes.txt`:
   ```bash
   git add src/notes.txt
   git commit -m "docs: complete assignment release checklist"
   ```
6. Create an **annotated tag** named `v1.0.0` at the current commit:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0 of Git practice assignment"
   ```

---

### Task 6: GitHub Collaboration Reflection (15 Points)
*Lecture Mapped: Lecture 6 - GitHub, PRs, and Remote Workflows*

1. Open `GITHUB_REFLECTION.md`.
2. Provide thoughtful 2-3 sentence answers to each of the 3 reflection questions on:
   - Difference between `git fetch` and `git pull`.
   - Purpose of Pull Requests (PRs) and peer code reviews.
   - Benefits of feature branching in multi-developer teams.
3. Commit your reflection:
   ```bash
   git add GITHUB_REFLECTION.md
   git commit -m "docs: complete GitHub reflection responses"
   ```

---

## 📤 Submission & Automated Feedback Guide

### Step 1: Verify your grade locally
Run the autograder locally on your development machine at any time to ensure you score **100/100 points**:
```bash
python autograder.py
```

### Step 2: Merge feature branches into main & push to GitHub
Ensure all your completed feature branches are merged into your local `main` branch, then push all branches and tags to your forked repository:
```bash
git checkout main
git merge feature/calculator
git merge feature/conflict-fix
git push origin main --tags
git push origin --all
```


### Step 3: Open a Pull Request (PR) to the Instructor Repository
1. Navigate to your forked repository page on GitHub (`https://github.com/<your-github-username>/Git_GitHub-Practice-Asgnmt`).
2. Click the **Contribute** dropdown button near the top right of your file list (next to *Fetch upstream*).
3. Click **Open pull request**.
4. Verify that:
   - **Base repository**: `ClassroomAsignments/Git_GitHub-Practice-Asgnmt` (branch: `main`)
   - **Head repository**: `<your-github-username>/Git_GitHub-Practice-Asgnmt` (branch: `main` or your submission branch)
5. Title your Pull Request as: `Submission: <Your Name> (<Your Student ID>)`.
6. Click **Create pull request**.

### Step 4: View your automated score table in PR comments
1. Once your Pull Request is opened, GitHub Actions automatically runs the central autograder suite.
2. Within **~15–20 seconds**, an automated bot will post an **Itemized Markdown Grade Score Table** directly in your PR conversation comments showing your itemized breakdown for Tasks 1 through 6.
3. **Updating your submission**: If you need to fix any task, simply make changes locally, commit, and push to your fork (`git push origin main`). Your PR score table comment will **automatically update in-place** with your new score!

