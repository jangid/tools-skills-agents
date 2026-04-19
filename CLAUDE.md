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

This repo includes a four-phase SDD workflow as skills:

1. `sdd-requirements` — elicit and document requirements (`docs/requirements.md`)
2. `sdd-specs` — translate requirements into design specs (`docs/spec/`)
3. `sdd-plan` — break specs into ordered implementation tasks
4. `sdd-implement` — execute the plan, verify against specs

Use these skills in order when building non-trivial features for any project.
