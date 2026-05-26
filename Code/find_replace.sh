#!/usr/bin/env zsh

# Usage: ./replace.sh <directory> <search> <replace>
dir="${1:-.}"
search="$2"
replace="$3"

if [[ -z "$search" ]]; then
  echo "Usage: $0 [directory] <search> <replace>"
  exit 1
fi

# Find all .txt files recursively and replace in-place
local count=0
for f in "$dir"/**/*.txt(N); do
  if grep -qF "$search" "$f"; then
    sed -i '' "s|${search}|${replace}|g" "$f"
    echo "Updated: $f"
    ((count++))
  fi
done

echo "\nDone. $count file(s) modified."