#!/bin/bash
# Auto-format Python files after Edit/Write operations using Taskfile
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ]; then
    exit 0
fi

case "$FILE_PATH" in
    *.py)
        task lint-file FILE="$FILE_PATH" 2>/dev/null
        ;;
esac
exit 0
