"""Test script for the MCP Git Branch Agent."""

import requests
import json


def test_git_branch_list():
    print("\n=== Test: git_branch_list ===")
    response = requests.post(
        "http://127.0.0.1:8001/mcp/tools/call",
        json={
            "name": "git_branch_list",
            "arguments": {},
        }
    )
    print(json.dumps(json.loads(response.text), indent=2))


def test_git_branch_create():
    print("\n=== Test: git_branch_create ===")
    response = requests.post(
        "http://127.0.0.1:8001/mcp/tools/call",
        json={
            "name": "git_branch_create",
            "arguments": {
                "name": "feat-test-mcp",
            },
        }
    )
    print(json.dumps(json.loads(response.text), indent=2))


def test_git_branch_status():
    print("\n=== Test: git_branch_status ===")
    response = requests.post(
        "http://127.0.0.1:8001/mcp/tools/call",
        json={
            "name": "git_branch_status",
            "arguments": {},
        }
    )
    print(json.dumps(json.loads(response.text), indent=2))


def test_git_branch_delete():
    print("\n=== Test: git_branch_delete ===")
    response = requests.post(
        "http://127.0.0.1:8001/mcp/tools/call",
        json={
            "name": "git_branch_delete",
            "arguments": {
                "name": "feat-test-mcp",
            },
        }
    )
    print(json.dumps(json.loads(response.text), indent=2))


if __name__ == "__main__":
    try:
        test_git_branch_list()
        test_git_branch_create()
        test_git_branch_status()
        test_git_branch_delete()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
