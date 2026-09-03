#!/usr/bin/env bash
# PostToolUse(Edit|Write) 훅: 방금 수정된 파일이 .py면 python -m py_compile로 문법 오류를 즉시 잡는다.
# stdin으로 hook input JSON(tool_input.file_path 포함)을 받는다.
jq -r '.tool_input.file_path' | tr -d '\r' | {
  read -r f
  case "$f" in
    *.py) python -m py_compile "$f" ;;
  esac
}
