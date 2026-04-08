Initialize harness in the current project.

Steps:
1. Create directory structure:
   - `plans/` (for implementation plans)
   - `.harness/` (for task proofs and artifacts)
2. Copy this repo's `.claude/CLAUDE.md` to the project's `.claude/CLAUDE.md`
3. Copy this repo's `.claude/commands/` to the project's `.claude/commands/`
4. Copy `AGENTS.md` template to project root
5. Add `.harness/` to `.gitignore`
6. Detect project type (check for next.config.*, tsconfig.json, package.json scripts)
7. Output what was installed and any project-specific notes

Arguments:
- $ARGUMENTS: optional project name (used in AGENTS.md header)
