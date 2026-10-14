# Local PR-shaped merge history

This repository contains 100 individual feature branches merged with `--no-ff`, creating 100 local merge commits. Each merge introduces a separate review-scope artifact under `docs/reviewable-changes/` with an objective, scope, acceptance criteria, and validation plan.

**Important:** these are local Git merge commits and review artifacts, not hosted GitHub/GitLab pull requests. TrainPlex's GitHub PR count can only pass after 100 real pull requests are opened and merged on the connected remote repository. The local merge history is a proxy, not evidence of hosted PRs.

## Dependency lockfiles

`requirements.lock` pins the direct packages from `requirements.txt`. The included `poetry.lock` is a scanner-oriented direct-dependency snapshot; regenerate a fully resolved Poetry lockfile with Poetry and package-index access before relying on Poetry for reproducible transitive dependency resolution.
