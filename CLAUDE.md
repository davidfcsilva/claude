# Claude Code Repository Baseline

## Overview

This repository is the **ultimate starting point** for any Claude-related project. Every `.claude/` feature (agents, skills, workflows, hooks, memory, templates) is pre-configured here as a reusable baseline.

For the authoritative master instructions, see **[`.claude/CLAUDE.md`](.claude/CLAUDE.md)**.

## Quick Start

### For a new project
```bash
# Copy the .claude directory to your project:
cp -r .claude /path/to/your/project/

# Then customize CLAUDE.md and any agents/skills for your specific needs.
```

### Use `/init-project` 
Run the `/init-project` slash command from `.claude/commands/init-project.md` to scaffold a complete Claude-enhanced repository in one step.

## Directory Structure

| Path | Purpose |
|------|---------|
| `.claude/CLAUDE.md` | Master instructions for all Claude Code features |
| `.claude/AGENTS.md` | Quick-reference index of agent types |
| `.claude/agents/` | Individual agent definitions (code-reviewer, planner, explorer, researcher) |
| `.claude/skills/` | Reusable skill templates (init, review, security-review, verify, run, dataviz) |
| `.claude/workflows/` | Multi-agent workflow templates (init-project, thorough-code-review, research-task, test-verify) |
| `.claude/hooks/` | Hook patterns (stop, enter-exit) |
| `.claude/commands/` | Custom slash command definitions |
| `.claude/memory/` | Memory system templates and index |
| `.claude/templates/` | Templates for creating new agents, skills, workflows, hooks |
| `.claude/settings.local.json` | Permission presets and environment config |

## Feature Catalog

### Agents (4)
- **code-reviewer** -- Diff review across effort levels (low/medium/high/max)
- **planner** -- Implementation planning with trade-off analysis
- **explorer** -- Read-only fan-out searches across codebases
- **researcher** -- Deep web research with source verification

### Skills (6)
- **init** -- Initialize a new Claude-enhanced repo from this baseline
- **review** -- Multi-dimensional code review workflow
- **security-review** -- Security audit patterns
- **verify** -- End-to-end flow verification
- **run** -- Project app launch and observation
- **dataviz** -- Data visualization guidelines

### Workflows (4)
- **init-project** -- Scaffold a new repo from this baseline
- **thorough-code-review** -- Multi-dimensional adversarial review
- **research-task** -- Deep research with verification
- **test-verify** -- Test execution + flow verification

### Hooks & Commands
- **Stop hook** -- Long-running task stop conditions
- **Enter/Exit hooks** -- Plan mode and worktree transitions
- **/init-project** -- Custom scaffold command

## Composition Tips

1. **Single agent** for focused, self-contained tasks
2. **Workflow** (Workflow tool) when you need deterministic orchestration across multiple agents
3. **Skills** to encapsulate reusable patterns within a single agent call
4. **Memory** files for persistent context across sessions
