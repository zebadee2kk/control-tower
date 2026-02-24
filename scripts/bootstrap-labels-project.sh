#!/usr/bin/env bash
# Idempotent bootstrap script for GitHub labels and Project v2 setup
# Requirements: gh CLI (https://cli.github.com/) with authentication

set -euo pipefail

REPO="zebadee2kk/control-tower"
PROJECT_NAME="Control Tower"

# --- 1. Create all 16 labels with exact names/colors from Issue #1 ---
# Define labels as: name|color|description
LABELS=(
  "state:research|0969DA|Investigation phase"
  "state:planning|0969DA|Design phase"
  "state:build|0969DA|Implementation"
  "state:awaiting-decision|0969DA|Needs approval"
  "state:blocked|0969DA|External blocker"
  "state:done|0969DA|Completed"
  "p0|D73A4A|Critical, blocking"
  "p1|E99695|High value"
  "p2|FBCA04|Normal"
  "p3|D4C5F9|Parked"
  "gate:allowed|8250DF|Proceed freely"
  "gate:needs-approval|8250DF|Decision required"
  "gate:paused|8250DF|On hold"
  "agent:research|1A7F37|Research agent task"
  "agent:build|1A7F37|Build agent task"
  "agent:finance|1A7F37|Finance agent task"
)

echo "Creating/updating labels..."
for entry in "${LABELS[@]}"; do
  IFS='|' read -r name color description <<< "$entry"
  # Check if label exists
  if gh label list -R "$REPO" | grep -Fq "$name"; then
    # Update color/description
    gh label edit "$name" -R "$REPO" --color "$color" --description "$description" 2>/dev/null || true
    echo "  ✓ Updated: $name"
  else
    gh label create "$name" -R "$REPO" --color "$color" --description "$description" 2>/dev/null || true
    echo "  + Created: $name"
  fi
done

echo "✅ Labels complete."

# --- 2. Create Project v2 board if not exists ---
echo "Setting up Project board..."
PROJECT_ID=$(gh project list --owner zebadee2kk --format json 2>/dev/null | jq -r ".projects.nodes[] | select(.title == \"$PROJECT_NAME\") | .number" || echo "")

if [[ -z "$PROJECT_ID" ]]; then
  echo "Creating new project..."
  PROJECT_NUM=$(gh project create --owner zebadee2kk --title "$PROJECT_NAME" --format json 2>/dev/null | jq -r '.number' || echo "")
  if [[ -n "$PROJECT_NUM" ]]; then
    echo "  🆕 Project '$PROJECT_NAME' created (#$PROJECT_NUM)"
    PROJECT_ID="$PROJECT_NUM"
  else
    echo "  ⚠️  Could not create project. May need manual setup."
    PROJECT_ID=""
  fi
else
  echo "  ✅ Project '$PROJECT_NAME' exists (#$PROJECT_ID)"
fi

# --- 3. Link all open issues to the project ---
if [[ -n "$PROJECT_ID" ]]; then
  echo "Linking issues to project..."
  open_issues=$(gh issue list -R "$REPO" --state open --json number --jq '.[].number' 2>/dev/null || echo "")
  if [[ -n "$open_issues" ]]; then
    for issue in $open_issues; do
      gh project item-add "$PROJECT_ID" --owner zebadee2kk --url "https://github.com/$REPO/issues/$issue" 2>/dev/null && echo "  🔗 Linked issue #$issue" || echo "  ✓ Issue #$issue already linked"
    done
    echo "✅ All open issues processed."
  else
    echo "  No open issues found."
  fi
else
  echo "  ⚠️  Skipping issue linking (no project ID)"
fi

echo ""
echo "🎉 Bootstrap complete!"
echo ""
echo "Next steps:"
echo "1. Visit https://github.com/zebadee2kk/control-tower/labels to see your labels"
echo "2. Visit https://github.com/zebadee2kk/control-tower/projects to configure your board"
echo "3. Add custom fields manually: Priority, Gate, Budget Cap, Spend-to-Date"
echo "4. Create tonight's Decision Desk issue"
