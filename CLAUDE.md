# Tools, Skills & Agents

A curated collection of reusable tools, skills, and agents for AI-assisted workflows.

## Repository Structure

```
tools/    — Standalone utilities and helper scripts
skills/   — Composable skill definitions (Claude Code SKILL.md format)
agents/   — Agent configurations and prompt templates
```

## Conventions

### Skills (`skills/`)

Each skill lives in its own directory with a `SKILL.md` file:

```
skills/<skill-name>/SKILL.md
```

- **Frontmatter** is required: `name`, `description` (YAML `---` block)
- `name` must match the directory name
- `description` is a concise sentence used for skill discovery — be specific about when to use vs. when to skip
- Body defines the skill's instructions, process, and rules
- Skills describe workflows, not implementation code
- Keep each SKILL.md under ~500 lines; split large skills into phases or sub-skills

### Agents (`agents/`)

Each agent is a single Markdown file:

```
agents/<agent-name>.md
```

- **Frontmatter** fields: `name`, `description`, `tools`, `model`, `color`, `emoji`, `vibe`
- `tools` lists the Claude Code tools the agent may use (e.g., `Read, Bash, Grep, Glob`)
- `model` specifies the preferred model tier (`opus`, `sonnet`, `haiku`)
- Body defines the agent's identity, phases, checklists, and report templates
- Agents are adversarial or specialized personas — they should be opinionated and thorough

### Tools (`tools/`)

Standalone scripts or utilities. Use the appropriate language for the task. Each tool should:

- Be self-contained (minimal dependencies)
- Include a usage comment or `--help` flag
- Follow the code style conventions from the user's global CLAUDE.md

## Adding New Content

### New Skill

1. Create `skills/<name>/SKILL.md` with frontmatter and body
2. Test the skill by invoking it in a Claude Code session
3. Commit with: `feat(skills): add <name>`

### New Agent

1. Create `agents/<name>.md` with frontmatter and body
2. Verify the agent can be loaded as a subagent type
3. Commit with: `feat(agents): add <name>`

### New Tool

1. Create the script in `tools/`
2. Ensure it runs standalone
3. Commit with: `feat(tools): add <name>`

## Quality Checks

- All Markdown files should be well-formed (no broken frontmatter)
- Skill and agent names use kebab-case
- No orphaned files — every skill directory has a SKILL.md, every agent file has frontmatter
- Descriptions must be actionable: state when to use AND when not to use

## Spec-Driven Development (SDD)

A cyclic, phase-based workflow for building software with AI assistance. Each phase produces artifacts on disk that serve as state markers — any new session can detect the current phase and resume.

### Phases (7 skills)

```
┌─ RESEARCH ──→ REQUIREMENTS ──→ SPECS ──→ PLAN ──→ IMPLEMENT ──→ VERIFY ─┐
│      ↑              ↑                                  │           │      │
│      └──────────────┴──────────── REPLAN ←─────────────┴───────────┘      │
└───────────────────────────────────────────────────────────────────────────┘
```

1. `sdd-research` — time-boxed exploration to reduce uncertainty (`docs/research/`)
2. `sdd-requirements` — elicit and document requirements (`docs/requirements.md`)
3. `sdd-specs` — translate requirements into design specs (`docs/spec/`)
4. `sdd-plan` — break specs into ordered, typed tasks (implement/spike/verify)
5. `sdd-implement` — execute the plan with TDD inner loop and stuck detection
6. `sdd-verify` — holistic validation: quality gates + acceptance criteria + UX
7. `sdd-replan` — structured replanning when assumptions break

### Phase Detection

Every skill detects the current phase on entry by checking which artifacts exist **and whether they are stale**:

| Artifact | Phase complete |
|----------|---------------|
| `docs/research/{topic}.md` (status: Complete) | Research done |
| `docs/requirements.md` (status: Approved) | Requirements done |
| `docs/spec/*.md` (all status: Approved) | Specs done |
| `docs/plan.md` (exists, tasks incomplete) | Planning done, implementing |
| `docs/plan.md` (all tasks done) | Implementation done |
| `docs/verification.md` (status: pass) | Verified, ready to ship |
| `docs/verification.md` (status: fail) | Needs replan |

#### Staleness Detection

Downstream artifacts become stale when their upstream inputs are updated. Each skill compares `last_updated` dates across the dependency chain:

```
research → requirements → specs → plan → implementation → verification
```

If a downstream artifact's `last_updated` is older than its upstream input, it is **stale** and needs updating — not skipping to. For example, if `requirements.md` was rewritten today but `docs/spec/*.md` and `docs/plan.md` are from last week, `sdd-specs` will update the specs rather than redirecting to `sdd-implement`. Early-phase skills (research, requirements) are always valid entry points — they note existing downstream artifacts but don't block on them.

### Key Differences from Linear Waterfall

- **Research phase**: explore before committing (time-boxed spikes)
- **Typed tasks**: implement (code), spike (research), verify (validation)
- **Stuck detection**: if implementation hits a wall, trigger replan instead of spinning
- **Replan triggers**: defined upfront in the plan — conditions that invalidate the approach
- **Holistic verification**: goes beyond "tests pass" to user-perspective validation
- **Cyclic**: replan can route back to any earlier phase based on severity

### When to Use

Use SDD for non-trivial features (multi-file, multi-day, architectural impact). Skip for bug fixes, small tweaks, and well-understood changes.
