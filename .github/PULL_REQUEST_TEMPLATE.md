## Description

<!-- A clear summary of what this PR does and why. Link any related issues. -->

Closes #<!-- issue number -->

## Type of Change

- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change (requires major version bump)
- [ ] Documentation only
- [ ] Refactor / code quality (no behavior change)
- [ ] CI / tooling

## Safety Review

> **Skip this section if the PR does not touch crisis detection, keyword lists, classifier thresholds, or the AI pipeline.**

- [ ] I have verified that genuine crisis keywords still trigger the crisis protocol
- [ ] I have verified that short/ambiguous messages ("yes", "okay") do NOT trigger false positives
- [ ] I have explained the threshold change rationale in the PR description

## Testing

- [ ] Unit tests pass: `python -m pytest tests/test_ai_pipeline.py -v`
- [ ] E2E tests pass (if applicable): `python tests/e2e_test.py`
- [ ] Manually tested: describe what you tested

## Checklist

- [ ] Code follows the existing style
- [ ] No secrets, debug prints, or temporary files included
- [ ] Documentation updated (README, API.md, ARCHITECTURE.md) if applicable
- [ ] CHANGELOG.md updated under `[Unreleased]`
