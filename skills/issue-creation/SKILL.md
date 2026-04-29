---
name: issue-creation
description: "Enforce issue-first discipline — no PR without an approved issue"
license: Apache-2.0
adapted-from: gentleman-programming/gentle-ai
version: "1.0"
load_when:
  - creating_github_issue
  - reporting_bug
  - requesting_feature
  - before_any_implementation
inputs:
  - name: issue_type
    type: enum
    enum: [bug, feature]
    required: true
  - name: description
    type: string
    required: true
outputs:
  - name: issue_url
    type: string
    format: "https://github.com/{owner}/{repo}/issues/{N}"
  - name: issue_number
    type: string
    format: "#{N} — used in PR body as Closes #{N}"
constraints:
  - blank_issues_disabled_must_use_template
  - status_approved_required_before_any_pr
  - search_duplicates_before_creating
  - questions_go_to_discussions_not_issues
---

# Issue Creation Skill

## When to Use

Load this skill whenever you need to:
- Report a bug in the current project
- Request a new feature or enhancement
- Create any GitHub issue before starting implementation

## Critical Rules

1. **No work begins without an approved issue** — `status:approved` is REQUIRED before opening any PR or branch.
2. **`status:needs-review` is applied automatically** — do NOT add it manually.
3. **No duplicate issues** — search existing issues before creating.
4. **Questions go to Discussions** — NOT issues.
5. **No Co-Authored-By trailers** — never add AI attribution.

## Workflow

```
1. Detect current repo
   REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

2. Search for existing issues → confirm no duplicate
   gh issue list --repo $REPO --state all --search "keywords"

3. Choose template: Bug → bug_report | Feature → feature_request

4. Submit issue → status:needs-review auto-applied

5. WAIT for status:approved from a maintainer

6. Only AFTER status:approved → create branch + open PR
```

> ⚠️ STOP after step 4. Do NOT open a PR until the issue has `status:approved`.

---

## Commands

```bash
# Detect repo
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

# Search existing issues
gh issue list --repo $REPO --state all --search "your keywords"

# Create bug report
gh issue create --repo $REPO \
  --title "fix(<scope>): <short description>" \
  --body "$(cat <<'EOF'
## Bug Description
[Clear description of the bug]

## Steps to Reproduce
1. 
2. 
3. 

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: 
- Version: 
EOF
)"

# Create feature request
gh issue create --repo $REPO \
  --title "feat(<scope>): <short description>" \
  --body "$(cat <<'EOF'
## Problem Statement
[Describe the problem this feature solves]

## Proposed Solution
[Specific description of the solution]

## Alternatives Considered
[Other approaches you thought about]
EOF
)"

# Check issue status
gh issue view <N> --repo $REPO --json title,labels -q '{title: .title, labels: [.labels[].name]}'
```

---

## Status Labels

| Label | Who applies |
|-------|------------|
| `status:needs-review` | Auto (on creation) |
| `status:approved` | Maintainer only — work can begin |
| `status:in-progress` | Contributor |
| `status:blocked` | Maintainer / Contributor |
| `status:wont-fix` | Maintainer only |

---

## Decision Tree

```
Question or idea to discuss?
├── YES → GitHub Discussions (NOT issues)
└── NO  → Is it a defect?
          ├── YES → Bug report
          └── NO  → Feature request
                    │
                    ▼
          Duplicate exists?
          ├── YES → Comment on existing issue
          └── NO  → Submit → wait for status:approved
```
