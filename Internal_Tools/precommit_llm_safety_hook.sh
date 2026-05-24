#!/usr/bin/env bash
# Simple pre-commit hook to flag obviously unsafe LLM-related content.
# Install by symlinking or copying into .git/hooks/pre-commit and making it executable.

set -euo pipefail

# Files to scan (prompts, docs, datasets). Use NUL separators because this
# workspace intentionally contains folder names with spaces.
mapfile -d '' FILES < <(
  git diff --cached --name-only -z --diff-filter=ACM -- \
    '*.md' '*.prompt' '*.txt' '*.jsonl' '*.yaml' '*.yml'
)

if [ "${#FILES[@]}" -eq 0 ]; then
  exit 0
fi

# Very simple pattern list - tuned to catch obviously offensive framing,
# not legitimate defensive usage in NorthStar's fraud/ransomware-prevention docs.
UNSAFE_PATTERNS=(
  "reverse shell"
  "keylogger"
  "botnet"
  "ddos attack"
  "ransomware payload"
  "ransomware builder"
  "exploit this server"
  "how do I hack"
)

FAIL=0

for file in "${FILES[@]}"; do
  # Skip internal policy/system prompt files themselves
  if [[ "$file" == 6.\ Internal_Strategy/LLM_* ]] || [[ "$file" == Internal_Strategy/LLM_* ]]; then
    continue
  fi

  for pattern in "${UNSAFE_PATTERNS[@]}"; do
    if grep -qi -- "$pattern" "$file"; then
      echo "LLM safety pre-commit: found unsafe pattern in $file: \"$pattern\""
      FAIL=1
    fi
  done
done

if [ "$FAIL" -ne 0 ]; then
  echo
  echo "Commit blocked by LLM safety hook."
  echo "If this is a false positive, rephrase to defensive/test-scenario language or document it in policy files."
  exit 1
fi

exit 0
