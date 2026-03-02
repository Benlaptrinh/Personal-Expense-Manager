# Contributing Guide

## Branching

- Use short topic branches: `feat/<scope>`, `fix/<scope>`, `chore/<scope>`.
- Keep pull requests focused to a single concern.

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/) with clear scope:

- `feat(auth): add refresh token rotation`
- `fix(expenses): enforce user ownership on update`
- `test(stats): cover cache invalidation flow`
- `chore(docker): align api service environment`
- `docs(readme): update local run instructions`

Format:

```text
<type>(<scope>): <summary>
```

Rules:

- Use imperative mood (`add`, `fix`, `remove`, `refactor`).
- Summary should be concise and specific.
- Prefer one logical change per commit.
- Include tests in the same commit when behavior changes.

## Pull Request Checklist

- [ ] Code builds locally
- [ ] Relevant tests pass
- [ ] API changes are reflected in docs/README
- [ ] No generated files (`node_modules`, `dist`, `venv`, `*.tsbuildinfo`, `*.db`) are committed
