#!/usr/bin/env bash
# Idempotent bootstrap script for GitHub labels and Project v2 setup
# Requirements: gh CLI (https://cli.github.com/) with required extensions and authentication

set -euo pipefail

REPO="zebadee2kk/control-tower"
PROJECT_NAME="Control Tower"

# --- 1. Create all 16 labels with exact names/colors from Issue #1 ---
# Define labels as: name|color|description
LABELS=(
  "bug|d73a4a|Something isn't working"
  "documentation|0075ca|Improvements or additions to documentation"
  "duplicate|cfd3d7|This issue or pull request already exists"
  "enhancement|a2eeef|New feature or request"
  "good first issue|7057ff|Good for newcomers"
  "help wanted|008672|Extra attention is needed"
  "invalid|e4e669|This doesn't seem right"
  "question|d876e3|Further information is requested"
  "wontfix|ffffff|This will not be worked on"
  "priority: high|b60205|High priority issue"
  "priority: medium|fbca04|Medium priority issue"
  "priority: low|0e8a16|Low priority issue"
  "gate: design|5319e7|Design phase gate"
  "gate: build|1d76db|Build phase gate"
  "gate: test|0e8a16|Test phase gate"
  "gate: deploy|e99695|Deploy phase gate"
)

for entry in "${LABELS[@]}"; do
  IFS='|' read -r name color description <<< "$entry"
  # Check if label exists
  if gh label list -R "$REPO" | grep -Fq "$name"; then
    # Update color/description if needed
    gh label edit "$name" -R "$REPO" --color "$color" --description "$description" >/dev/null
  else
    gh label create "$name" -R "$REPO" --color "$color" --description "$description" >/dev/null
  fi
done

echo "✅ Labels ensured."

# --- 2. Create Project v2 board if not exists ---
PROJECT_ID=$(gh project list --owner zebadee2kk --format json | jq -r ".[] | select(.title == \"$PROJECT_NAME\") | .id")
if [[ -z "$PROJECT_ID" ]]; then
  PROJECT_ID=$(gh project create --owner zebadee2kk --title "$PROJECT_NAME" --format json | jq -r '.id')
  echo "🆕 Project '$PROJECT_NAME' created."
else
  echo "✅ Project '$PROJECT_NAME' exists."
fi

# --- 3. Add custom fields if not present ---
# Helper: Add single-select field if missing
gh_project_field_ensure() {
  local project_id="$1"; local field_name="$2"; local field_type="$3"; shift 3; local options=("$@")
  local exists=$(gh project field-list "$project_id" --format json | jq -r ".[] | select(.name == \"$field_name\") | .id")
  if [[ -z "$exists" ]]; then
    if [[ "$field_type" == "single_select" ]]; then
      gh project field-create "$project_id" --name "$field_name" --data-type SINGLE_SELECT --options "${options[*]}" >/dev/null
    else
      gh project field-create "$project_id" --name "$field_name" --data-type "$field_type" >/dev/null
    fi
    echo "🆕 Field '$field_name' created."
  else
    echo "✅ Field '$field_name' exists."
  fi
}

gh_project_field_ensure "$PROJECT_ID" "Priority" single_select "High,Medium,Low"
gh_project_field_ensure "$PROJECT_ID" "Gate" single_select "Design,Build,Test,Deploy"
gh_project_field_ensure "$PROJECT_ID" "Budget Cap" text

gh_project_field_ensure "$PROJECT_ID" "Spend-to-Date" text

# --- 4. Link all open issues to the project ---
open_issues=$(gh issue list -R "$REPO" --state open --json number --jq '.[].number')
for issue in $open_issues; do
  # Check if already linked
  if ! gh project item-list "$PROJECT_ID" --format json | jq -e ".[] | select(.content.number == $issue)" >/dev/null; then
    gh project item-add "$PROJECT_ID" --url "https://github.com/$REPO/issues/$issue" >/dev/null
    echo "🔗 Linked issue #$issue to project."
  fi
done

echo "✅ All open issues linked."

# --- 5. Add automation: move to 'Done' when closed ---
# Note: As of 2026, GitHub Projects v2 automation is limited via API/CLI. This step is a placeholder for when automation is available.
# If automation is available, insert the CLI/API call here.
echo "⚠️  Please manually configure automation to move issues to 'Done' when closed, as this is not yet supported via gh CLI."

echo "🎉 Bootstrap complete."
