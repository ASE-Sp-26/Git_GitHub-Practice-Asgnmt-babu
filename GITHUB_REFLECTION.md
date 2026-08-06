# GitHub & Git Practice Assignment - Student Reflection

Please answer the following questions after completing Tasks 1 through 5.

### 1. What is the difference between `git fetch` and `git pull`?
`git fetch` downloads the latest remote commits, branches, and refs from the remote repository to your local Git tracking references without modifying your working tree files. On the other hand, `git pull` is a combination of `git fetch` followed immediately by `git merge`, bringing remote changes directly into your active working branch. Using `git fetch` allows developers to safely review remote updates before merging them.

### 2. How did you resolve the merge conflict in Task 4?
To resolve the merge conflict in Task 4, I ran `git merge feature/conflict-fix` while on the `main` branch, which flagged conflicting changes in `src/app.py`. I opened `src/app.py` in my code editor, inspected the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`), combined the desired code changes cleanly, and deleted all conflict markers. Finally, I staged the resolved file using `git add src/app.py` and finalized the merge with a clean commit `git commit -m "fix: resolve merge conflict in src/app.py"`.

### 3. Why is it useful to use `.gitignore` in a software project?
Using `.gitignore` is essential for keeping repositories clean and protecting sensitive or unnecessary files from being tracked by Git. It prevents build artifacts, log files, temporary environment folders, and secret configuration files from bloating the repository history. This ensures smooth collaboration among team members without file conflicts or security breaches.
