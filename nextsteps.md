# Next Steps — Claude Code Setup Optimization

Based on a comprehensive review of the [claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) repository (8 documents across CLI flags, commands, MCP servers, memory, settings, skills, sub-agents, and power-ups) and an audit of your current project state.

## Current State Summary

| Area | Status | Notes |
|------|--------|-------|
| Root `CLAUDE.md` | Strong | Well-structured with rules, conventions, project context |
| Settings | Bloated | 232-line allowlist in `settings.local.json` — violates "use deterministic harness settings, not memory/preferences" principle |
| MCP Servers | Missing | No `.mcp.json` — best-practice recommends Context7, Playwright, DeepWiki as daily drivers |
| Skills | Good foundation | 3 custom skills (git-vcs, k8s-troubleshoot, k8s-observability) + bundled skills |
| Sub-agents | 1 custom | `saas-architect` — well-designed with memory system |
| Memory | Empty | `.claude/memory/` not yet populated |
| Worktrees | Not used | Best-practice recommends for isolated feature work |

---

## Priority 1: Clean up settings.local.json permission allowlist

**Problem:** Your `settings.local.json` has 232 permission entries accumulated from every command ever run. Best-practice says: keep settings concise (under 200 lines recommended), use broad patterns, and leverage `fewer-permission-prompts` skill to generate a prioritized, minimal allowlist.

**Action:**
- Run `/fewer-permission-prompts` to let Claude analyze your transcripts and generate a prioritized allowlist based on actual recurring patterns
- Replace the 232 verbatim entries with wildcard patterns:
  ```json
  {
    "permissions": {
      "allow": [
        "Bash(git *)",
        "Bash(kubectl *)",
        "Bash(python *)",
        "Bash(pip *)",
        "Bash(curl *)",
        "Bash(ssh *)",
        "Bash(scp *)",
        "Read(f:/claude/**)",
        "Read(c:/users/dsilva/.claude/**)",
        "WebFetch(domain:github.com)",
        "WebFetch(domain:raw.githubusercontent.com)",
        "WebSearch"
      ]
    }
  }
  ```
- Consider setting `permissionMode` to `"auto"` or `"acceptEdits"` for faster workflows on trusted projects

---

## Priority 2: Set up MCP servers

**Problem:** No `.mcp.json` found. The best-practice guide identifies 5 daily-use MCP servers:

| Tool | Purpose | Verdict for You |
|------|---------|-----------------|
| **Context7** | Current docs to avoid hallucination | High priority — you work with k8s, FastAPI, ArgoCD APIs |
| **DeepWiki** | Repository documentation retrieval | Medium — your codebase grows; useful for cross-project reference |
| **Playwright** | Browser automation / UI testing | Medium — you test web apps (argocddemo frontend) |
| **Claude in Chrome** | Real-time DOM inspection | Low-Medium — complements Playwright |
| **Excalidraw** | Architecture diagrams | Low — saas-architect agent could benefit |

**Action:**
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "deepwiki": {
      "command": "npx",
      "args": ["-y", "deepwiki-mcp"]
    }
  }
}
```
Write this to `.claude/.mcp.json` (project-level, committed to repo per best-practice scope hierarchy).

---

## Priority 3: Adopt worktree workflow for feature isolation

**Problem:** You're working directly on the `development` branch. Best-practice recommends `-w` / `--worktree` flag for isolated git branches, preventing accidental commits and enabling parallel feature development.

**Action:**
- Start sessions with `claude -w` to get an isolated worktree branch
- Or use `/vcs branch create feat/what-youre-working-on` (your git-vcs skill already supports this) before making changes
- Your saas-architect agent definition already has `isolation: "worktree"` in frontmatter — extend this pattern

---

## Priority 4: Populate project memory

**Problem:** `.claude/memory/` is empty. The best-practice guide emphasizes memory for: user profile, feedback (corrections confirmed), project context, and external references.

**Immediate memories to save:**
- **User memory:** Your role (DevOps/Kubernetes developer working with ArgoCD, k3s, FastAPI)
- **Project memory:** argocddemo deployment lifecycle (spec-driven), k3s cluster details (192.168.50.220, no Helm), observability stack plan
- **Reference memory:** k3s cluster SSH access, ArgoCD dashboard URL, best-practice repo URL

---

## Priority 5: Consolidate skills with proper frontmatter

**Problem:** Your custom skills (git-vcs, k8s-troubleshoot, k8s-observability) are well-built but missing recommended frontmatter fields. Best-practice says skills should have: `name`, `description`, `when_to_use`, `paths`, and `user-invocable`.

**Action for each SKILL.md:** Add frontmatter header:
```yaml
---
name: "k8s-troubleshoot"
description: "Kubernetes cluster troubleshooting — argocddemo namespace operations"
when_to_use: "When debugging pods, services, deployments, or network policies in the k3s cluster. Triggered by 'kubectl', 'pod not running', 'service unreachable', 'network policy'."
paths:
  - "argocddemo/k8s/**"
  - "bin/k8s-troubleshoot"
user-invocable: true
---
```

---

## Priority 6: Session hygiene — context management

Best-practice findings applied to your workflow:
- **"New task = new session"** prevents cross-contamination. You tend to run multi-topic sessions (k8s debugging + architecture design + git ops). Use `/clear` between distinct tasks.
- **Rewind > correct:** When patches fail, use `/rewind` instead of stacking corrective prompts — keeps context lean
- **Keep context under 40% capacity** for quality outputs. Monitor with `/context` command

---

## Priority 7: Explore power-ups you haven't used

You have access to 10 interactive lessons (`/powerup`). Most relevant unexplored ones:
1. **"Multiply yourself"** — subagent orchestration (you have saas-architect but could add more)
2. **"Automate your workflow"** — hooks for PreToolUse/PostToolUse events
3. **"Undo anything"** — `/rewind` and checkpointing

---

## Priority 8: Add effort/model control to custom agents

**Current:** Your saas-architect agent inherits model. Best-practice says to pin models strategically:
- Heavy analysis/architecture → `opus` or `sonnet` with `effort: high`
- Mechanical exploration → `haiku`
- Your Explore-equivalent searches should use Haiku to save tokens

**Action:** Add `model: "sonnet"` and `effort: "high"` to saas-architect frontmatter if you want consistent quality, or leave as inherit but control via `/effort` command.

---

## Implementation Order

1. **Immediate (5 min):** Compress `settings.local.json` to wildcard patterns
2. **This session:** Create `.claude/.mcp.json` with Context7 + DeepWiki
3. **Next session:** Save 3-4 core memories to `.claude/memory/`
4. **Ongoing:** Add frontmatter to existing skills as you update them
5. **When starting features:** Use worktree or branch-first workflow

---

## Sources Absorbed

All 8 documents from `shanraisshan/claude-code-best-practice/best-practice/`:
- `claude-cli-startup-flags.md` — CLI parameters and session management
- `claude-commands.md` — 16 frontmatter fields + 86 built-in slash commands
- `claude-mcp.md` — MCP server recommendations, setup, permissions, scope hierarchy
- `claude-memory.md` — Context file handling, monorepo patterns, two-retrieval methods
- `claude-power-ups.md` — 10 interactive feature lessons
- `claude-settings.md` — Settings hierarchy (5 levels), permissions, model routing, sandbox
- `claude-skills.md` — Skill frontmatter, 13 bundled skills, official skills repo
- `claude-subagents.md` — Subagent frontmatter (16 fields), 5 built-in agent types

Plus README: context hygiene rules ("dumb zone" at 40% capacity, "rewind > correct", "new task = new session"), prompting best practices, config management principles.
