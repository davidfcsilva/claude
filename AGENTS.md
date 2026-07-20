# Available Agents

This repo ships the following agent types. Each is defined in `.claude/agents/<name>.md` with full operating instructions.

| Agent | Trigger | Definition |
|---|---|---|
| `code-reviewer` | Review diffs for bugs, reuse, simplification, efficiency | [agents/code-reviewer.md](./agents/code-reviewer.md) |
| `planner` | Design implementation plans with trade-off analysis | [agents/planner.md](./agents/planner.md) |
| `explorer` | Read-only broad fan-out searches across many files | [agents/explorer.md](./agents/explorer.md) |
| `researcher` | Deep, multi-source research with claim verification | [agents/researcher.md](./agents/researcher.md) |

### Built-in agents (Claude Code platform agents)

These are shipped by the Claude Code runtime — you don't define them here, but they're listed for completeness:

| Agent | Purpose |
|---|---|
| `general-purpose` | Catch-all for any task that doesn't match a specialized agent |
| `claude-code-guide` | Questions about Claude Code features, hooks, SDK, API, Tag |
| `Explore` | Read-only search for broad file sweeps (no edits) |
| `Plan` | Architecture and implementation planning (platform version) |

### Agent selection guide

Use this decision flow to pick an agent:

```
Does the task need codebase knowledge?
  → No, it's external/factual → researcher
  → Yes, it needs files read/written → continue below

Is this a single-focused task?
  → Code changes/bugs → code-reviewer
  → Planning/design → planner (or built-in Plan)
  → Test strategy → spawn a tester agent

Does the task need to read many files without modifying anything?
  → explorer or built-in Explore

Does the task orchestrate multiple agents or skills?
  → Use a workflow instead of a single agent
```

### Adding new agents

To add an agent:
1. Create `.claude/agents/<name>.md` with the format described in the templates above
2. Add a row to this table
3. Test by spawning it with `Agent` tool
