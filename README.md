# Claude Code Repository Baseline

The ultimate starting point for any Claude-related repository. A comprehensive structure covering every Claude Code feature that delivers value from day one.

## What This Is

This repo contains pre-built, production-ready configurations for all major Claude Code features:

- **Agents** — Pre-tuned agent definitions for code review, planning, exploration, and research
- **Skills** — Reusable skill templates encapsulating domain-specific workflows
- **Workflows** — Multi-agent orchestration patterns with deterministic control flow
- **Hooks** — Stop, Enter/Exit, and Command hook patterns
- **Memory** — Memory system templates and index for persistent context
- **Templates** — Ready-to-use templates for creating new features

Every file is written for immediate use — no placeholders, no "TODO" stubs.

## Quick Start

### Use as a template repo
1. Click "Use this template" or fork this repo
2. Clone your copy locally
3. Customize `.claude/CLAUDE.md` for your project's needs
4. Add agents/skills/workflows as needed using the templates in `.claude/templates/`

### Copy to an existing project
```bash
# From this repo, into any other project:
cp -r .claude /path/to/target-project/
cp CLAUDE.md README.md /path/to/target-project/
```

Then edit `.claude/CLAUDE.md` to customize the master instructions for your specific domain.

## Directory Structure

```
.claude/
├── CLAUDE.md                 ← Master project instructions (read this first)
├── AGENTS.md                 ← Agent quick-reference index
├── agents/                   ← Individual agent definitions
│   ├── code-reviewer.md      ← Review diffs for bugs, reuse, efficiency
│   ├── planner.md            ← Design implementation plans with trade-offs
│   ├── explorer.md           ← Read-only fan-out searches
│   └── researcher.md         ← Deep web research with verification
├── skills/                   ← Reusable skill templates
│   ├── init.md               ← Scaffold new Claude-enhanced repo
│   ├── review.md             ← Multi-dimensional code review
│   ├── security-review.md    ← Security audit patterns
│   ├── verify.md             ← End-to-end flow verification
│   ├── run.md                ← Project app launch patterns
│   └── dataviz.md            ← Data visualization guidelines
├── workflows/                ← Multi-agent orchestration templates
│   ├── init-project.md       ← Scaffold new repo (4-phase)
│   ├── thorough-code-review.md ← Adversarial review pipeline
│   ├── research-task.md      ← Deep research with verification
│   └── test-verify.md        ← Test execution + flow verification
├── hooks/                    ← Hook patterns
│   ├── stop.md               ← Stop condition patterns
│   └── commands/             ← Custom slash command definitions
│       └── init-project.sh
├── memory/                   ← Memory system
│   ├── MEMORY.md             ← Memory index template
│   └── templates/            ← Memory template files
│       ├── project-overview.md
│       └── architecture-decision.md
├── templates/                ← Create new feature templates
│   ├── agent-template.md     ← New agent definition
│   ├── skill-template.md     ← New skill definition
│   ├── workflow-template.md  ← New workflow definition
│   └── hook-template.md      ← New hook definition
├── commands/                 ← Slash command definitions
│   └── init-project.md       ← /init-project command
└── settings.local.json       ← Permission presets & env config

CLAUDE.md                     ← Root quick-reference (mirror of .claude/CLAUDE.md)
README.md                     ← This file
```

## Feature Catalog

### Agents

| Agent | When to Use | Effort Level |
|-------|-------------|-------------|
| **code-reviewer** | Review diffs, check for bugs and simplifications | low/medium/high/max |
| **planner** | Before starting non-trivial implementation | high |
| **explorer** | Read-only searches across many files or directories | medium |
| **researcher** | Deep research on any topic with web sources | medium |

### Skills

| Skill | Trigger | Output |
|-------|---------|--------|
| **init** | New repo needs Claude integration | Scaffolds CLAUDE.md, agents, skills, workflows |
| **review** | "Review these changes" / "Check the diff" | Findings by category: bugs, reuse, efficiency |
| **security-review** | Security audit request | Vulnerability report with exploitability scores |
| **verify** | "Verify this works" after code change | End-to-end flow verification results |
| **run** | "Run the app" / "Start the dev server" | App process output and observation notes |
| **dataviz** | Any data visualization need | Chart specs, color palettes, accessibility checks |

### Workflows

| Workflow | Phases | Use When |
|----------|--------|----------|
| **init-project** | 4 phases | Scaffolding a new Claude-enhanced repo |
| **thorough-code-review** | Find → Dedup → Verify → Synthesize | Comprehensive multi-dimensional review |
| **research-task** | Search → Fetch → Verify → Report | Fact-checked research report needed |
| **test-verify** | Discover → Execute → Verify → Summarize | Tests + flow verification after changes |

### Hooks

| Hook | Purpose | Control |
|------|---------|---------|
| **Stop** | Stop long-running tasks with conditions | `/goal clear` to clear early |
| **Enter/Exit** | Plan mode and worktree transitions | Manual via ExitPlanMode / ExitWorktree |
| **Commands** | Custom slash commands | `/init-project`, etc. |

## How to Customize

### For your specific project domain
1. Edit `.claude/CLAUDE.md` — update the skill descriptions, add domain-specific agent prompts
2. Add agents in `.claude/agents/` using `templates/agent-template.md`
3. Add skills in `.claude/skills/` using `templates/skill-template.md`
4. Add workflows in `.claude/workflows/` using `templates/workflow-template.md`

### For different project types
| Project Type | Customize These |
|-------------|----------------|
| **Web app** | Skills: run (server patterns), verify (browser testing) |
| **CLI tool** | Skills: run (CLI launch patterns), agents: tester |
| **Library** | Skills: review, workflow: test-verify (npm/pip test commands) |
| **Data pipeline** | Agents: researcher (data schema research), skills: verify (output validation) |
| **ML/AI project** | Agents: researcher (model comparison), skills: dataviz (evaluation metrics) |

## Best Practices

### Agent Selection
- **Agent for focused tasks**, Workflow for multi-agent orchestration
- Use `pipeline()` by default, `parallel()` only when items genuinely need independent processing
- Use schemas for structured output — they validate at the tool-call layer

### Skill Composition
1. Start with a skill to encapsulate a pattern
2. Add agents within the skill if sub-tasks are complex
3. Escalate to workflow only when you need deterministic multi-agent control flow

### Memory System
- Use `user` type for who-the-user-is facts
- Use `feedback` type for corrections and confirmed approaches (include Why and How to apply)
- Use `project` type for ongoing work constraints not derivable from code
- Use `reference` type for URLs, dashboards, tickets
- Always link related memories with `[[name]]` syntax
- Update the MEMORY.md index when adding entries

### Workflows
- Define `meta.name`, `meta.description`, and `meta.phases` in every workflow script
- Guard loops on `budget.total` to avoid unbounded agent spawning
- Use `log()` to report what was dropped in bounded coverage scenarios
- Script body is plain JavaScript — no TypeScript type annotations

## Contributing Patterns

When adding a new feature to this baseline:
1. Write the definition file
2. Update the index (`AGENTS.md`, skills list in CLAUDE.md, workflow table)
3. Add it to README.md's Feature Catalog table
4. Update MEMORY.md if it's significant project context
5. Use a template from `.claude/templates/` as your starting point

## License

This baseline is provided as-is — use and modify freely for any Claude-related project.
