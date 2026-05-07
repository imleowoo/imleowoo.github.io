#!/usr/bin/env python3
"""Format code blocks in markdown posts by language type."""

import re
import subprocess
import sys
from pathlib import Path

POSTS_DIR = Path("/Users/leiwu/Projects/imleowoo.github.io/content/posts")

# Map language identifiers to formatter commands.
# Each formatter takes code via stdin and outputs formatted code to stdout.
FORMATTERS = {
    "python": ["ruff", "format", "--line-length", "100", "-"],
    "py": ["ruff", "format", "--line-length", "100", "-"],
    # shell/bash blocks often contain command output, not scripts — skip
    "c": ["clang-format", "--style", "Microsoft"],
    "h": ["clang-format", "--style", "Microsoft"],
}

# Languages we skip entirely (not code, or already formatted)
SKIP_LANGUAGES = {"text", "diff", "requirements", "ini", "toml", "yaml", "yml", "json", "xml", "csv", ""}


def extract_prefix(line: str) -> str:
    """Extract the prefix (whitespace + optional blockquote marker) before the code fence."""
    match = re.match(r"^(\s*>?\s*)", line)
    return match.group(1) if match else ""


def format_code(code: str, lang: str) -> str | None:
    """Run the formatter for the given language. Returns formatted code or None on failure."""
    cmd = FORMATTERS.get(lang)
    if cmd is None:
        return None
    try:
        result = subprocess.run(
            cmd,
            input=code,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout:
            # Strip trailing newline added by formatters (we'll add it back uniformly)
            formatted = result.stdout
            if formatted.endswith("\n"):
                formatted = formatted[:-1]
            return formatted
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def process_file(filepath: Path) -> bool:
    """Process a single markdown file. Returns True if any changes were made."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    changed = False
    i = 0
    new_lines = []

    while i < len(lines):
        line = lines[i]

        # Check if this line contains a fenced code block opener: ```lang
        match = re.match(r"^(\s*>?\s*)(```+)(\w*)\s*$", line)
        if not match:
            new_lines.append(line)
            i += 1
            continue

        prefix = match.group(1)
        backticks = match.group(2)
        lang = match.group(3).lower().strip()

        # Collect the code block content
        code_lines = []
        j = i + 1
        found_close = False
        while j < len(lines):
            close_match = re.match(
                r"^" + re.escape(prefix) + re.escape(backticks) + r"\s*$", lines[j]
            )
            if close_match:
                found_close = True
                break
            # Strip the prefix from code lines
            code_line = lines[j]
            if prefix and code_line.startswith(prefix):
                code_line = code_line[len(prefix):]
            code_lines.append(code_line)
            j += 1

        if not found_close:
            # Malformed block — skip
            new_lines.append(line)
            i += 1
            continue

        original_code = "".join(code_lines)

        # Skip if language is not something we format
        if lang in SKIP_LANGUAGES:
            new_lines.append(line)
            new_lines.extend(lines[i + 1 : j + 1])
            i = j + 1
            continue

        if lang not in FORMATTERS:
            new_lines.append(line)
            new_lines.extend(lines[i + 1 : j + 1])
            i = j + 1
            continue

        # Try to format
        formatted = format_code(original_code, lang)

        if formatted is None or formatted == original_code:
            # Formatting failed or no change
            new_lines.append(line)
            new_lines.extend(lines[i + 1 : j + 1])
            i = j + 1
            continue

        # Replace the block with formatted code
        new_lines.append(line)  # opening fence
        for fline in formatted.split("\n"):
            new_lines.append(prefix + fline + "\n")
        new_lines.append(prefix + backticks + "\n")  # closing fence

        changed = True
        i = j + 1

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True
    return False


def main():
    changed_files = []
    unchanged_files = []

    for post_dir in sorted(POSTS_DIR.iterdir()):
        if not post_dir.is_dir():
            continue
        index_file = post_dir / "index.md"
        if not index_file.exists():
            continue

        try:
            if process_file(index_file):
                changed_files.append(str(index_file.relative_to(POSTS_DIR.parent)))
            else:
                unchanged_files.append(str(index_file.relative_to(POSTS_DIR.parent)))
        except Exception as e:
            print(f"Error processing {index_file}: {e}", file=sys.stderr)

    print(f"Changed: {len(changed_files)} files")
    for f in changed_files:
        print(f"  ✓ {f}")
    print(f"Unchanged: {len(unchanged_files)} files")


if __name__ == "__main__":
    main()
