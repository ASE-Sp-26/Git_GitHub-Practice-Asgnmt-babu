# Git & GitHub Practice Assignment: Grading Rubric

**Course:** Advanced Software Engineering (ASE)  
**Total Grade:** 100 Points  

---

## 📊 Evaluation Matrix

| Task ID & Title | Max Points | Exemplary (Full Credit) | Satisfactory (Partial Credit) | Unsatisfactory (0 Credit) |
|---|---|---|---|---|
| **Task 1: Git Config & Student Info** | **15 Points** | `student_info.json` populated with student name, ID, and GitHub username; Git commit author email matches configured identity. <br>*(15 pts)* | `student_info.json` updated but Git commit author email is unverified or generic. <br>*(10 pts)* | `student_info.json` contains unedited placeholder text or file is missing. <br>*(0 pts)* |
| **Task 2: `.gitignore` Configuration** | **15 Points** | `.gitignore` contains explicit rules for `*.log`, `temp/`, `lectures/`; no log or build artifacts tracked in Git index. <br>*(15 pts)* | `.gitignore` contains some rules but misses `temp/` or `*.log`; or untracked files clutter workspace. <br>*(8 pts)* | `.gitignore` unedited or temporary/log files tracked in Git repository. <br>*(0 pts)* |
| **Task 3: Branching & Feature Development** | **20 Points** | Branch `feature/calculator` created; `add(a,b)` and `multiply(a,b)` implemented in `src/calculator.py`; clean commit message. <br>*(20 pts)* | Code implemented on `main` instead of `feature/calculator` branch, or function math contains minor bugs. <br>*(10 pts)* | Functions not implemented, or syntax errors prevent code execution. <br>*(0 pts)* |
| **Task 4: Merge Conflict Resolution** | **20 Points** | `feature/conflict-fix` branch merged into `main`; conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) completely removed; `src/app.py` executes cleanly. <br>*(20 pts)* | Conflict merged, but conflict markers or syntax errors left behind in `src/app.py`. <br>*(10 pts)* | Merge not attempted or unresolved conflict blocks execution. <br>*(0 pts)* |
| **Task 5: Git Stashing & Release Tagging** | **15 Points** | Stashed checklist changes applied to `src/notes.txt` with all items checked `[x]`; annotated Git release tag `v1.0.0` created. <br>*(15 pts)* | Release tag created as lightweight tag instead of annotated tag, or stash incomplete. <br>*(8 pts)* | Tag `v1.0.0` missing and checklist uncompleted. <br>*(0 pts)* |
| **Task 6: GitHub Reflection** | **15 Points** | `GITHUB_REFLECTION.md` completed thoroughly answering all 3 questions regarding remotes, PRs, and code review strategies. <br>*(15 pts)* | Reflection file submitted but responses are brief (under 2 sentences per question). <br>*(8 pts)* | Reflection file blank or contains placeholder text. <br>*(0 pts)* |

---

## 💡 Common Deductions & Late Submission Policy
- **Unresolved Conflict Markers**: -10 points if conflict marker strings (`<<<<<<<`, `=======`, `>>>>>>>`) are committed to Git.
- **Untracked Log Files**: -5 points if log files or `temp/` build artifacts are tracked in the repository history.
- **Local Testing**: Running `python autograder.py` before submission guarantees accurate score feedback!
