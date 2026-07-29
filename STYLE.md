# Style Guide — Claude Code Repository Baseline

This file defines the coding, documentation, and output style conventions that guide every artifact produced in this repository — source code, agent prompts, skill definitions, workflow scripts, hooks, memories, templates, and documentation.

## Why This Exists

Consistent style reduces cognitive load for both humans and Claude when reading, reviewing, or generating code across projects. When every file follows the same conventions, patterns emerge automatically and errors become visually obvious. Use this guide whenever writing or reviewing any artifact in this repo.

## General Principles

1. **Readability first** — Code and prose should be readable without context. A new team member should understand it within 30 seconds.
2. **Convention over configuration** — Default to the style already established in surrounding code. When no precedent exists, follow the conventions below.
3. **Minimal is better** — No unnecessary abstractions, comments, or indirection. Every line should earn its place.
4. **Explicit over implicit** — Name things for their behavior, not their implementation. Make edge cases explicit rather than hidden in comments.

## Source Code Style

### File Organization

```
project/
├── src/
│   ├── index.ts                    # Entry point — exports public API only
│   ├── config/                     # Configuration (typed defaults + runtime override)
│   ├── routes/                     # HTTP route handlers (one file per resource)
│   ├── services/                   # Business logic (no I/O directly, use interfaces)
│   ├── models/                     # Data models / entities
│   ├── utils/                      # Shared utilities (only if used by 2+ modules)
│   └── types/                      # TypeScript type definitions (if non-trivial)
├── tests/                          # All test files (co-located or separate — pick one per project)
│   ├── integration/
│   └── unit/
├── docs/                           # Documentation (architecture decisions, API specs)
├── scripts/                        # One-off automation scripts
└── package.json
```

### Naming Conventions

| Category | Convention | Example |
|----------|-----------|---------|
| Files (TypeScript) | `camelCaseWithDots` for modules; `PascalCase` for components/classes | `userService.ts`, `Avatar.tsx` |
| Files (Python) | `snake_case` | `user_service.py` |
| Variables | `camelCase` (TS/JS), `snake_case` (Python) | `userName`, `user_count` |
| Functions/Methods | `camelCase`, verb-first | `getUserById()`, `calculate_total()` |
| Classes/Types | `PascalCase` | `UserService`, `DatabasePool` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT_MS` |
| Interfaces (TS) | `PascalCase` or prefixed with `I` per project convention | `UserRepository` / `IUserService` |
| Environment Variables | `UPPER_SNAKE_CASE` | `DATABASE_URL`, `REDIS_HOST` |
| Test functions | Describe the behavior: `{function} should {expected outcome}` | `getUserById returns null for missing user` |

### Code Organization Within Functions

```typescript
// 1. Input validation (guard clauses — fail fast)
if (!input) throw new ValidationError("Input is required");
if (input.length > MAX_LENGTH) throw new ValidationError(`Max length is ${MAX_LENGTH}`);

// 2. Setup (preconditions, dependencies)
const cache = getCache();
if (cache.has(input.id)) return cache.get(input.id);

// 3. Core logic (the "happy path" — the main thing this function does)
const result = await fetchFromDatabase(input);

// 4. Post-processing (side effects, caching, cleanup)
cache.set(input.id, result, { ttl: CACHE_TTL });
return result;
```

### Comments

- **Why, not what** — Don't comment code that explains itself. Comment the intent behind it.
- **Use JSDoc/TSDoc for public APIs** — Every exported function needs a description and parameter docs.
  ```typescript
  /**
   * Resolves a user by their unique identifier.
   * @param id - The user's UUID (v4)
   * @returns The user object, or null if not found
   * @throws ValidationError if id is malformed
   */
  export async function getUserById(id: string): Promise<User | null> {
  ```
- **Inline comments** — Only when the "why" isn't obvious from the code. One sentence per comment. Avoid trailing whitespace after comments.

### Error Handling

```typescript
// Prefer specific error types over generic Error
throw new ValidationError("Invalid email format");    // for validation failures
throw new NotFoundError(`User ${id} not found`);       // for expected absences
throw new RuntimeError("Connection pool exhausted");   // for unexpected system state

// Use try/catch at the boundary, not everywhere
try {
  await processPayment(order);
} catch (err) {
  logger.error({ err }, "Payment processing failed");
  throw new PaymentError(`Failed to process order ${order.id}`);
}
```

### Async / Concurrency

- Use `Promise.all()` for independent operations in parallel (not sequential `await`s)
- Set timeouts on all external calls: `{ signal: AbortSignal.timeout(5000) }`
- Document concurrency assumptions explicitly (e.g., "this function is not idempotent")

## Documentation Style

### CLAUDE.md / README.md

- Write for Claude first, human second — be specific enough that an agent can follow instructions without guessing
- Use tables for structured data (feature catalogs, options comparisons)
- Use code blocks for examples with proper language tags
- Keep sections under 100 lines when possible; break longer content into sub-files

### Commit Messages

```
<type>: <subject line>

<body if needed — explain why, not what>

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`

**Rules:**
- Subject line: imperative mood, lowercase, no period, max 72 characters
- Body wraps at 72 characters
- Separate subject from body with a blank line

### PR Descriptions

```markdown
## What
[Brief description of what changed]

## Why
[Reason for the change — links to issue/ticket if applicable]

## Changes
- `src/a.ts`: Added X feature
- `src/b.ts`: Refactored Y for clarity

## Testing
- Unit tests added for new functions
- Manual: tested with sample data including edge case Z
```

## Output Style (Agent / Claude Code)

### Responses

- **Code first** — When the user asks for code, show it before explaining it
- **Tables over lists** — When comparing options, use tables not bullet lists
- **One idea per paragraph** — Don't cram multiple concepts into a single block of text
- **Skip preamble** — Don't start with "Here's..." or "I'd be happy to...". Just deliver the answer

### Code Blocks

- Always include the language tag: ````typescript`, not just ````
- Show the minimal relevant snippet — don't dump entire files unless asked
- For diffs, use standard unified diff format when comparing versions

## Workflow Script Style

All `.claude/workflows/*.md` JavaScript scripts follow these conventions:

```javascript
// Use meaningful constant names (SCREAMING_SNAKE for configuration values)
const MAX_FINDINGS = 10;
const VERIFY_MIN_VOTES = 2;

// Schema definitions go first, then logic
const FINDINGS_SCHEMA = { /* ... */ };

// Use pipeline() by default, parallel() only when genuinely needed
const results = await pipeline(
  items,
  item => transform(item),        // Inline transforms are fine for simple ops
  result => validate(result)        // Step functions should be named where possible
);

// Log what was dropped in bounded coverage scenarios
log(`${results.length} of ${items.length} findings confirmed`);
```

- **No TypeScript annotations** — Scripts run as plain JavaScript
- **No `Date.now()` / `Math.random()`** — These break resume; pass timestamps via args instead
- **Use `.filter(Boolean)`** on all pipeline/parallel results to handle null drops
- **Guard loops on `budget.total`** to prevent unbounded agent spawning

## Memory File Style

Memory files in `.claude/memory/` use this format:

```markdown
---
name: <short-kebab-case-slug>
description: <one-line summary used to decide relevance during recall>
metadata:
  type: user | feedback | project | reference
---

<the fact; for feedback include Why and How to apply lines. Link related memories with [[name]].>
```

**Rules:**
- `name`: short, kebab-case, ≤40 characters
- `description`: ≤120 characters, optimized for search relevance
- Body: one paragraph max unless it's a structured record (ADR)
- Always link related memories: `[[related-memory-name]]`

## Review Criteria

When the `review` skill or `code-reviewer` agent evaluates code, use these checks:

| Check | What to Look For | Severity |
|-------|-----------------|----------|
| **Correctness** | Off-by-one errors, null dereferences, type mismatches, race conditions, N+1 queries | high |
| **Reuse** | Duplicated logic that could be extracted, over-specific code that should be generic | medium |
| **Simplification** | Unnecessary indirection, complex conditionals that could be guards, dead code | medium |
| **Efficiency** | Inefficient data structures, avoidable re-computation, missing indexes | medium |
| **Security** | Injection vectors, auth bypasses, information leaks, unsafe deserialization | high |
| **Test coverage** | Uncovered branches in changed code, no regression tests for bug fixes | low |

## Customization Per Project

This baseline style guide is a starting point. Customize it by editing this file:

- Add language-specific conventions that differ from the defaults above
- Add project-specific directory structure deviations (e.g., NestJS modules, Next.js app router)
- Add team-specific naming preferences in a `## Team Conventions` section
- Link to linter/formatter configs that enforce these rules programmatically (`.eslintrc`, `.prettierrc`, `pyproject.toml`, etc.)
