"""
Local Git Branching Agent

This agent manages git branches for local Development workflows.
It can be invoked via MCP or command line.
"""

import subprocess
import json
import sys
import os
from datetime import datetime
from typing import Optional


class GitBranchAgent:
    """Local agent for git branch management."""

    from datetime import datetime

    def __init__(
        self,
        repo_path: Optional[str] = None,
        branch_prefix: str = "feat",
        default_branch: str = "main",
        cleanup_on_merge: bool = True,
    ):
        """Initialize agent."""
        self.repo_path = repo_path or os.getcwd()
        self.branch_prefix = branch_prefix
        self.default_branch = default_branch
        self.cleanup_on_merge = cleanup_on_merge
        self._changedir(self.repo_path)

    def _changedir(self, path: str):
        """Change to repo directory."""
        if not os.path.isdir(path):
            raise ValueError(f"Path not found: {path}")
        os.chdir(path)

    def _run(self, args: list) -> tuple:
        """Run git command."""
        cmd = ["git"] + args
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)

    # Branch listing
    def list_branches(self) -> list:
        """List all branches with stats."""
        code, stdout, _ = self._run(["--list", "--format",
            f'%(refname:short) \t%(objectname:short) \t%ad %D',
            f'--sort=-committerdate', '--date=short'])

        if code != 0:
            return []

        branches = []
        for line in stdout.strip().split("\n"):
            if line:
                parts = line.split("\t", 2)
                branches.append({
                    "name": parts[0] if len(parts) > 0 else "",
                    "sha": parts[1] if len(parts) > 1 else "",
                    "remote": parts[2] if len(parts) > 2 else "",
                    "updated": datetime.fromisoformat(parts[3].rstrip()) if len(parts) > 3 else None,
                })

        return branches

    # Branch creation
    def create_branch(
        self,
        name: str,
        source: Optional[str] = None,
        force: bool = False,
    ) -> bool:
        """Create a new branch."""
        if name.startswith(self.branch_prefix):
            branches = [b["name"] for b in self.list_branches()]
            if name in branches:
                print(f"Branch '{name}' already exists")
                return False

        if source is None:
            source = self.default_branch

        args = ["checkout", "-b", name]
        if source != self.default_branch:
            args.append(source)

        code, stdout, _ = self._run(args)
        return code == 0

    # Branch deletion
    def delete_branch(self, name: str, force: bool = False) -> bool:
        """Delete a branch."""
        args = ["branch", "-d", name]
        if force:
            args.append("--force")

        code, stdout, _ = self._run(args)
        return code == 0

    # Branch merge
    def merge_branch(
        self,
        branch: str,
        strategy: str = "normal",
    ) -> dict:
        """Merge a branch into current."""
        if branch == self.default_branch:
            print("Cannot merge main into itself")
            return {"success": False, "error": "Cannot merge main into itself"}

        args = ["merge", branch]
        if strategy == "no-ff":
            args.append("--no-ff")
        elif strategy == "ff":
            args.append("--ff")
        elif strategy == "squash":
            args.append("--squash")

        # Get current branch
        current = [b["name"] for b in self.list_branches() if not b["remote"]][0]

        # Add commit message
        args.append(f"-m 'Merge {branch} into {current}'")

        code, stdout, _ = self._run(args)

        # Cleanup
        if self.cleanup_on_merge and code == 0:
            self.delete_branch(branch, force=True)

        return {
            "success": code == 0,
            "message": stdout.strip() if code == 0 else str(_),
        }

    # Status
    def status(self) -> dict:
        """Get branch status."""
        branches = self.list_branches()

        stale = [b for b in branches if b["name"] != self.default_branch and b["name"] != "HEAD"]
        open_branches = [b for b in branches if not b["remote"]]

        return {
            "current_branch": [b["name"] for b in branches if not b["remote"]][0] if branches else None,
            "total_branches": len(branches),
            "stale_branches": len(stale),
            "open_branches": len(open_branches),
            "branches": branches,
            "stale": stale,
            "open": open_branches,
        }


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Git Branch Management Agent")
    parser.add_argument("--repo", default=None, help="Repository path")
    parser.add_argument("--prefix", default="feat", help="Branch prefix")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup on merge")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # List
    subparsers.add_parser("list", help="List branches")

    # Create
    create_parser = subparsers.add_parser("create", help="Create branch")
    create_parser.add_argument("name", help="Branch name")
    create_parser.add_argument("--source", help="Source branch")
    create_parser.add_argument("--force", action="store_true", help="Force create")

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete branch")
    delete_parser.add_argument("name", help="Branch name")
    delete_parser.add_argument("--force", action="store_true", help="Force delete")

    # Merge
    merge_parser = subparsers.add_parser("merge", help="Merge branch")
    merge_parser.add_argument("branch", help="Branch to merge")
    merge_parser.add_argument("--strategy", choices=["normal", "no-ff", "squash"], default="normal")

    # Status
    subparsers.add_parser("status", help="Show branch status")

    # Cleanup
    subparsers.add_parser("cleanup", help="Delete merged branches")

    args = parser.parse_args()
    agent = GitBranchAgent(repo_path=args.repo, branch_prefix=args.prefix, cleanup_on_merge=args.cleanup)

    if args.command == "list":
        for b in agent.list_branches():
            print(b)
    elif args.command == "create":
        success = agent.create_branch(args.name, source=args.source)
        print(f"Created: {success}")
    elif args.command == "delete":
        success = agent.delete_branch(args.name, force=args.force)
        print(f"Deleted: {success}")
    elif args.command == "merge":
        result = agent.merge_branch(args.branch, strategy=args.strategy)
        print(result)
    elif args.command == "status":
        status = agent.status()
        print(json.dumps(status, indent=2, default=str))
    elif args.command == "cleanup":
        stale = [b["name"] for b in agent.list_branches() if not b["remote"]]
        deleted = [b["name"] for b in stale if agent.delete_branch(b["name"], force=True)]
        print(f"Deleted {len(deleted)} branches")


if __name__ == "__main__":
    main()
