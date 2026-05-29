"""
MCP Server for Git Branch Management

This server exposes git branch management capabilities to MCP clients.
"""

import asyncio
import argparse
import json
import os
import subprocess
from datetime import datetime
from typing import Any, List, Optional

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import (
    CallToolResult,
    ContentBlock,
    TextContent,
    Tool,
)


class GitBranchAgent:
    """Git branch management agent."""

    def __init__(
        self,
        repo_path: Optional[str] = None,
        branch_prefix: str = "",
        default_branch: str = "main",
    ):
        self.repo_path = repo_path or os.getcwd()
        self.branch_prefix = branch_prefix
        self.default_branch = default_branch
        self._changedir(self.repo_path)

    def _changedir(self, path: str):
        if not os.path.isdir(path):
            raise ValueError(f"Path not found: {path}")
        os.chdir(path)

    def _run(self, args: List[str]) -> tuple:
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

    def list_branches(self) -> List[dict]:
        code, stdout, _ = self._run(
            ["--list", "--format", "%(refname:short) %(objectname:short) %ad %D", "--sort=-committerdate", "--date=short"]
        )
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
                })
        return branches

    def create_branch(
        self,
        name: str,
        source: Optional[str] = None,
        force: bool = False,
    ) -> bool:
        branches = [b["name"] for b in self.list_branches()]
        if name in branches:
            return False

        if source is None:
            source = self.default_branch

        args = ["checkout", "-b", name, source]
        code, stdout, _ = self._run(args)
        return code == 0

    def delete_branch(self, name: str, force: bool = False) -> bool:
        args = ["branch", "-d", name]
        if force:
            args.append("--force")
        code, stdout, _ = self._run(args)
        return code == 0

    def merge_branch(
        self,
        branch: str,
        strategy: str = "normal",
    ) -> dict:
        if branch == self.default_branch:
            return {"success": False, "error": "Cannot merge main into itself"}

        args = ["merge", branch]
        if strategy == "no-ff":
            args.append("--no-ff")
        elif strategy == "ff":
            args.append("--ff")
        elif strategy == "squash":
            args.append("--squash")
        args.append(f"-m 'Merge {branch}'")

        current = [b["name"] for b in self.list_branches() if not b["remote"]][0]
        code, stdout, _ = self._run(args)

        return {
            "success": code == 0,
            "message": stdout.strip() if code == 0 else str(_),
        }

    def status(self) -> dict:
        branches = self.list_branches()
        stale = [b for b in branches if b["name"] != self.default_branch]
        return {
            "branches": branches,
            "stale": stale,
        }


# Create MCP server
app = Server("git-branch-agent")


@app.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="git_branch_list",
            description="List all git branches with their SHA and remote info",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="git_branch_create",
            description="Create a new branch (can use any branch name without prefix)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Branch name (any name is allowed)",
                    },
                    "source": {
                        "type": "string",
                        "description": "Source branch to base on (optional, defaults to main)",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="git_branch_delete",
            description="Delete a git branch",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Branch name to delete",
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force delete (even if not fully merged)",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="git_branch_merge",
            description="Merge a branch into current branch",
            inputSchema={
                "type": "object",
                "properties": {
                    "branch": {
                        "type": "string",
                        "description": "Branch to merge",
                    },
                    "strategy": {
                        "type": "string",
                        "enum": ["normal", "no-ff", "ff", "squash"],
                        "description": "Merge strategy",
                    },
                },
                "required": ["branch"],
            },
        ),
        Tool(
            name="git_branch_status",
            description="Get branch status and list",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    try:
        agent = GitBranchAgent()

        if name == "git_branch_list":
            branches = agent.list_branches()
            return CallToolResult(
                content=[
                    ContentBlock(
                        type="text",
                        text=json.dumps(branches, indent=2),
                    )
                ]
            )

        elif name == "git_branch_create":
            name = arguments.get("name", "")
            source = arguments.get("source")
            success = agent.create_branch(name=name, source=source)
            message = f"Branch '{name}' created successfully" if success else f"Failed to create branch '{name}': {agent.list_branches()}"
            return CallToolResult(
                content=[
                    ContentBlock(
                        type="text",
                        text=json.dumps({"success": success, "message": message}),
                    )
                ]
            )

        elif name == "git_branch_delete":
            name = arguments.get("name", "")
            force = arguments.get("force", False)
            success = agent.delete_branch(name=name, force=force)
            return CallToolResult(
                content=[
                    ContentBlock(
                        type="text",
                        text=json.dumps({"success": success, "message": f"Branch '{name}' deleted" if success else f"Failed to delete branch: {name}"}),
                    )
                ]
            )

        elif name == "git_branch_merge":
            branch = arguments.get("branch", "")
            strategy = arguments.get("strategy", "normal")
            result = agent.merge_branch(branch=branch, strategy=strategy)
            return CallToolResult(
                content=[
                    ContentBlock(
                        type="text",
                        text=json.dumps(result),
                    )
                ]
            )

        elif name == "git_branch_status":
            status = agent.status()
            return CallToolResult(
                content=[
                    ContentBlock(
                        type="text",
                        text=json.dumps(status),
                    )
                ]
            )

        else:
            return CallToolResult(
                content=[
                    ContentBlock(
                        type="text",
                        text=json.dumps({"error": f"Unknown tool: {name}"}),
                    )
                ]
            )

    except Exception as e:
        return CallToolResult(
            content=[
                ContentBlock(
                    type="text",
                    text=json.dumps({"error": str(e)}),
                )
            ]
        )


def run_sse_server():
    """Run SSE server."""
    import threading

    host = "127.0.0.1"
    port = 8000

    transport = SseServerTransport(port)

    def handle_request(request):
        @app.request()
        async def mcp_request(request: Any) -> Any:
            return await transport.handle_request(request)

        return request

    def run_app():
        try:
            asyncio.run(app.run(transport=transport, lifespan="off"))
        except Exception as e:
            print(f"Error running server: {e}")

    thread = threading.Thread(target=run_app, daemon=True)
    thread.start()

    print(f"SSE server running at http://{host}:{port}")
    return f"http://{host}:{port}"


def run_cli():
    """Run CLI mode."""
    parser = argparse.ArgumentParser(description="MCP Git Branch Agent")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--mode", choices=["cli", "sse"], default="cli", help="Run mode")
    args = parser.parse_args()

    if args.mode == "sse":
        print(f"Starting SSE server at http://{args.host}:{args.port}")
        run_sse_server()
    else:
        # CLI mode for direct testing
        print("MCP Git Branch Agent")
        print("Use git commands directly or connect via MCP")
        return


if __name__ == "__main__":
    run_cli()
