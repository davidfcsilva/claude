# Claude Code Command Line Interface Manual

This document provides a comprehensive guide to the Claude Code command line interface.

## Getting Started

Install Claude Code using one of these methods:
- **Native Install (Recommended)**: `curl -fsSL https://claude.ai/install.sh | bash` (macOS, Linux, WSL)
- **Windows PowerShell**: `irm https://claude.ai/install.ps1 | iex`
- **Homebrew**: `brew install --cask claude-code`
- **WinGet**: `winget install Anthropic.ClaudeCode`

Start Claude Code in any project directory:
```bash
cd your-project
claude
```

## Core CLI Commands

### Starting Sessions
- `claude` - Start interactive session
- `claude "query"` - Start interactive session with initial prompt
- `claude -p "query"` - Query via SDK, then exit
- `cat file | claude -p "query"` - Process piped content

### Managing Conversations
- `claude -c` - Continue most recent conversation in current directory
- `claude -c -p "query"` - Continue via SDK
- `claude -r "" "query"` - Resume session by ID or name
- `claude --continue` - Alias for `claude -c`
- `claude --resume` - Resume a specific session

### Authentication
- `claude auth login` - Sign in to your Anthropic account
- `claude auth logout` - Log out from your Anthropic account
- `claude auth status` - Show authentication status

### Agent Management
- `claude agents` - List all configured subagents
- `claude auto-mode defaults` - Print built-in auto mode classifier rules

### Configuration
- `claude mcp` - Configure Model Context Protocol (MCP) servers
- `claude plugin` - Manage Claude Code plugins
- `claude setup-token` - Generate a long-lived OAuth token for CI and scripts

## Key Flags

### Session Control
- `--add-dir` - Add additional working directories for file access
- `--agent` - Specify an agent for the current session
- `--allow-dangerously-skip-permissions` - Add `bypassPermissions` to the permission mode cycle
- `--dangerously-skip-permissions` - Skip permission prompts (equivalent to `--permission-mode bypassPermissions`)

### Model Configuration
- `--effort` - Set the effort level (low, medium, high, xhigh, max)
- `--model` - Sets the model for the current session
- `--fallback-model` - Enable automatic fallback to specified model when default is overloaded

### Output and Debugging
- `--debug` - Enable debug mode with optional category filtering
- `--debug-file` - Write debug logs to a specific file path
- `--output-format` - Specify output format (text, json, stream-json)
- `--print`, `-p` - Print response without interactive mode

### Permission Control
- `--permission-mode` - Begin in a specified permission mode (default, acceptEdits, plan, auto, dontAsk, bypassPermissions)
- `--allowedTools` - Tools that execute without prompting for permission
- `--disallowedTools` - Tools that are removed from the model's context

## Slash Commands (Inside Interactive Sessions)

### Session Management
- `/clear` - Start a new conversation with empty context
- `/compact` - Free up context by summarizing conversation
- `/exit` - Exit the CLI
- `/help` - Show help and available commands
- `/rename` - Rename the current session
- `/resume` - Resume a conversation by ID or name
- `/recap` - Generate a one-line summary of current session
- `/reset` - Alias for `/clear`
- `/new` - Alias for `/clear`

### Model and Context
- `/model` - Select or change the AI model
- `/effort` - Set the model effort level
- `/context` - Visualize current context usage
- `/compact` - Free up context by summarizing conversation

### Tools and Utilities
- `/batch` - Orchestrate large-scale changes across a codebase in parallel
- `/diff` - Open interactive diff viewer
- `/doctor` - Diagnose and verify Claude Code installation
- `/loop` - Run a prompt repeatedly on a schedule
- `/memory` - Edit memory files and manage auto-memory
- `/permissions` - Manage allow, ask, and deny rules for tool permissions
- `/plan` - Enter plan mode directly from the prompt
- `/review` - Review a pull request locally
- `/ultrareview` - Run a deep, multi-agent code review in cloud sandbox

### Advanced Features
- `/team-onboarding` - Generate a team onboarding guide from usage history
- `/fewer-permission-prompts` - Scan transcripts for common tool calls and add allowlist
- `/teleport` - Pull a web session into the terminal
- `/remote-control` - Make session available for remote control from claude.ai
- `/config` - Open settings interface to adjust preferences

## Advanced Usage Patterns

### Context Management
- Use `/compact` to free up context when working on complex tasks
- Use `/context` to visualize context usage and optimize performance
- Implement Team OS by structuring repositories with nested CLAUDE.md files

### Automation
- Use `/loop` for continuous monitoring of deployments or status checks
- Use `/batch` for parallelized code changes
- Set up `/schedule` for recurring tasks and routines

### Remote Control
- Use `/remote-control` to control Claude Code from Claude.ai or Claude app
- Use `/teleport` to pull web sessions into your terminal

### Performance Optimization
- Use `--bare` mode for scripted calls that start faster
- Use `--effort` flag to adjust speed vs. intelligence tradeoff
- Use `--model` to specify different models based on task requirements

## Best Practices

1. **Use the three-layer architecture**:
   - Core Layer: Main conversation window for orchestration
   - Delegation Layer: Subagents for heavy exploration
   - Extension Layer: MCP connections and hooks for toolchain integration

2. **Manage context effectively**:
   - Use `/compact` to prevent context window overflow
   - Use `/context` to monitor context usage
   - Implement Team OS for efficient context loading

3. **Leverage automation**:
   - Use `/loop` for monitoring tasks
   - Use `/batch` for parallelized code changes
   - Use `/schedule` for recurring tasks

4. **Secure operations**:
   - Use `/auto-mode` instead of `--dangerously-skip-permissions` for automation
   - Configure hooks for deterministic actions
   - Use `/permissions` to manage tool access rules

## Sources:
- [The Ultimate Claude Code CLI Deep Dive & Guide to the Newest Commands from April 2026 Release](https://medium.com/@jiten.p.oswal/the-ultimate-claude-code-cli-deep-dive-guide-to-the-newest-commands-from-april-2026-release-1eeb25b03c52)
- [CLI reference - Claude Code Docs](http://code.claude.com/docs/en/cli-reference)
- [Commands - Claude Code Docs](http://code.claude.com/docs/en/commands)
- [Claude Code overview - Claude Code Docs](https://docs.claude.com/docs/claude-code)
- [Claude Code by Anthropic | AI Coding Agent, Terminal, IDE](http://code.claude.com/en/cli-reference)