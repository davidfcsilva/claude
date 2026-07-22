---
name: git-vcs
description: "Version control management CLI with branch protection and conventional commit enforcement"
when_to_use: "When the user asks to manage version control, commit changes, create branches, merge, rebase, resolve conflicts, or inspect the git tree"
paths:
  - "bin/git-vcs"
user_invocable: true
---

# git-vcs — Version Control Management

When the user asks to manage version control, commit changes, create branches, merge, rebase, resolve conflicts, or inspect the git tree, invoke this skill. It provides a CLI for all git operations with built-in branch protection (refuses destructive operations on `main` or `master`).

## How to invoke

1. The CLI is at `bin/git-vcs` (relative to the repository root). Use it directly:

       bin/git-vcs <subcommand> [options]

   Or invoke via slash command in any chat:

       /vcs status
       /vcs commit feat "add login endpoint"
       /vcs merge development

2. All operations are scoped to the current repository (`git rev-parse --show-toplevel`).

## Subcommands

| Subcommand | Example | What it does |
|---|---|---|
| `status` | `/vcs status` | Show working tree status, staged changes, and branch info. |
| `tree [-L N] [--all]` | `/vcs tree -L 2 --all` | Visualize the commit history as a graph. Default: last 5 commits on current branch. Use `--all` for all branches. `-L N` controls depth. |
| `commit <type> <msg>` | `/vcs commit feat "add pagination"` | Stage all changes and commit with a conventional commit message (`<type>: <msg>`). Types: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `ci`. |
| `commit-amend [<type> <msg>]` | `/vcs commit-amend fix "update error handling"` | Amend the most recent commit. If no type/msg given, reuses the previous commit message. |
| `branch create <name>` | `/vcs branch create feat/user-profile` | Create a new branch from the current HEAD. |
| `branch switch <name>` | `/vcs branch switch development` | Switch to an existing local or remote-tracked branch (creates tracking if needed). |
| `branch list [--remote]` | `/vcs branch list --remote` | List local branches (current highlighted). Add `--remote` for remote-tracking branches. |
| `branch delete <name>` | `/vcs branch delete feat/old-feature` | Delete a branch. Refuses if the branch is unmerged. Use `-f` to force. |
| `branch rename <new>` | `/vcs branch rename feat/auth-login` | Rename the current branch. |
| `push [--force]` | `/vcs push` | Push current branch and its upstream. Sets up tracking on first push. |
| `pull [--rebase]` | `/vcs pull --rebase` | Pull from upstream. Add `--rebase` to rebase local commits instead of merging. |
| `merge <branch>` | `/vcs merge development` | Merge `<branch>` into the current branch. Aborts automatically on conflicts and prompts for resolution. |
| `rebase <branch>` | `/vcs rebase development` | Rebase current branch onto `<branch>`. On conflict, stops so you can resolve. |
| `conflict status` | `/vcs conflict status` | Show which files have unresolved merge/rebase conflicts. |
| `conflict resolve <file> [<mode>]` | `/vcs conflict resolve src/app.py ours` | Mark a conflict as resolved. Mode: `ours`, `theirs`, or `manual` (open editor). Stages the file. |
| `conflict continue` | `/vcs conflict continue` | Continue a paused merge or rebase after all conflicts are resolved. |
| `conflict abort` | `/vcs conflict abort` | Abort the current merge or rebase, returning to the pre-conflict state. |
| `log [--author <name>] [-n N] [--grep <pattern>]` | `/vcs log -n 10 --feat` | Show commit log filtered by type. Flags: `--feat`, `--fix`, `--refactor`, `--docs`, `--chore`, `--test`, `--ci`. |
| `diff [staged]` | `/vcs diff staged` | Show working-tree diff. Add `staged` for staged-only changes. |
| `stash [pop \| list]` | `/vcs stash list` | Stash, pop, or list stashed changes. Default: stash current working tree. |
| `tag [<name>] [-a -m "msg"]` | `/vcs tag v0.2.0 -a -m "Release v0.2.0"` | Create a tag. Lightweight by default; use `-a` for annotated. Omit `<name>` to list all tags. |
| `reset [soft \| mixed \| hard] [<ref>]` | `/vcs reset soft HEAD~1` | Reset current branch. Defaults to `mixed HEAD`. Shows warning for `hard`. |
| `info` | `/vcs info` | Show repo summary: remote URL, current branch, ahead/behind counts, last commit. |

## Branch Protection

The CLI enforces the following rules on protected branches (`main`, `master`):

- **No direct commit:** `commit` refuses if you are on `main` or `master`.
- **No force push:** `push --force` refuses on protected branches.
- **No hard reset:** `reset hard` refuses on protected branches.
- **No branch delete of protected branches.**

All other operations (status, log, diff, pull, etc.) work normally on protected branches.

## Conventional Commit Types

| Type | Meaning |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `docs` | Documentation only changes |
| `chore` | Maintenance, deps, tooling |
| `test` | Adding or correcting tests |
| `ci` | CI/CD configuration changes |

## Typical Workflow

### Start a new feature
```bash
/vcs branch create feat/user-auth          # Create branch from current HEAD
/vcs commit feat "add login endpoint"      # Commit your changes
/vcs push                                   # Push to remote with tracking
```

### Sync with development and merge
```bash
/vcs branch switch development             # Go back to development
/vcs pull --rebase                          # Update development
/vcs branch switch feat/user-auth           # Switch back to feature
/vcs rebase development                     # Rebuild feature on top of development
/vcs push --force                           # Force-push rebased branch
/vcs branch switch development              # Switch to development again
/vcs merge feat/user-auth                   # Merge feature in
```

### Resolve a conflict
```bash
/vcs merge feat/problematic-branch          # Start merge, it hits a conflict
/vcs conflict status                        # See which files are conflicted
/vcs conflict resolve src/app.py theirs     # Accept incoming for a file
/vcs conflict resolve tests/test_app.py manual  # Open editor for another
/vcs conflict continue                      # Finish the merge
```

## Exit codes

- **0**: success
- **1**: general error (invalid args, git command failed)
- **2**: branch protection violation (attempted dangerous op on main/master)
- **3**: conflict detected (merge/rebase stopped; use `conflict *` subcommands)
- **4**: not a git repository

## Related skills

- The `argocddemo-workflow` skill handles the spec-driven deployment lifecycle. This skill manages the version control layer that feeds into that workflow.
- The `k8s-troubleshoot` and `k8s-observability` skills manage cluster operations; this skill manages the code that defines those clusters.
