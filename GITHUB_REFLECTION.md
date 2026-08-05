# GitHub & Git Practice Assignment - Student Reflection

Please answer the following questions after completing Tasks 1 through 5.

### 1. What is the difference between `git fetch` and `git pull`?
`git fetch` downloads commits, files, and refs from a remote repository into your local repository without merging them into your current working branch. This allows you to inspect remote changes safely before integrating them. `git pull`, on the other hand, performs a `git fetch` followed immediately by a `git merge` (or `git rebase`), integrating remote changes directly into your active local working branch.

### 2. How did you resolve the merge conflict in Task 4?
To resolve the merge conflict in Task 4, I created the feature branch `feature/conflict-fix`, identified the conflicting files (`app.py` and `src/app.py`), and removed the Git conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`). I combined the desired function signatures and logic so `greet(name)` executes cleanly, tested the output locally, committed the resolution with a message containing `fix: resolve merge conflict`, and merged the branch into `main`.

### 3. Why is it useful to use `.gitignore` in a software project?
Using `.gitignore` prevents untracked temporary files, OS metadata, build outputs (like `__pycache__/` or `*.log`), secret configuration files, and heavy dependencies from being accidentally committed to Git. This keeps the repository clean, light, and secure, ensuring that collaborators and CI/CD pipelines only receive essential source code files.
