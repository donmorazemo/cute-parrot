# CLAUDE.md

## Project Overview

This is a test/demonstration Git repository (`cute-parrot`) used for practicing Git operations and collaborative development workflows. It contains plain text files rather than application source code.

## Repository Structure

```
cute-parrot/
├── README.md            # Project description
├── CLAUDE.md            # This file — guidance for AI assistants
├── TestFile1.txt        # Test file for Git operations
├── TestFile2.txt        # Test file for Git operations
└── TestFileLocal.txt    # Test file created locally
```

## Key Details

- **No build system** — there is no `package.json`, `Makefile`, or similar. No build or compile step is needed.
- **No dependencies** — no package manager or external libraries.
- **No test framework** — the `.txt` files are manual test artifacts, not automated tests.
- **No linting or formatting** — no ESLint, Prettier, or other code-quality tooling is configured.
- **No CI/CD** — no GitHub Actions, GitLab CI, or other pipelines.

## Git Conventions

- **Default branch**: `master`
- **Commit messages**: Short, imperative-style summaries (e.g., "Update TestFile1.txt", "My New File").
- **Branching**: Feature branches are used for changes (e.g., `claude/...` branches).

## Development Workflow

1. Create or switch to a feature branch.
2. Make changes to text files.
3. Commit with a clear, concise message.
4. Push to the remote and open a pull request if needed.

## Notes for AI Assistants

- This repository has no code to build, test, or lint. Do not attempt to run build or test commands.
- Changes are limited to text files and documentation.
- Keep commits small and descriptive.
