#!/usr/bin/env python3
"""Extract new Gemini conversation blocks after an old history boundary."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path


TIME_RE = re.compile(r"^message time:\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*$")
USER_MARKER = "you asked"
RESPONSE_MARKER = "gemini response"


@dataclass
class ConversationBlock:
    index: int
    start_line: int
    end_line: int
    time: str | None
    user_message: str
    gemini_response: str
    raw: str


def normalize_message(text: str) -> str:
    text = text.casefold()
    chars: list[str] = []
    for char in text:
        if unicodedata.category(char).startswith("P"):
            chars.append(" ")
        else:
            chars.append(char)
    return re.sub(r"\s+", " ", "".join(chars)).strip()


def parse_blocks(text: str) -> list[ConversationBlock]:
    lines = text.splitlines(keepends=True)
    starts = [
        index
        for index, line in enumerate(lines)
        if line.strip().casefold() == USER_MARKER
    ]
    blocks: list[ConversationBlock] = []

    for block_index, start in enumerate(starts):
        end = starts[block_index + 1] if block_index + 1 < len(starts) else len(lines)
        time_value: str | None = None
        response_index: int | None = None
        time_index: int | None = None

        for index in range(start + 1, end):
            stripped = lines[index].strip()
            time_match = TIME_RE.match(stripped)
            if time_value is None and time_match:
                time_value = time_match.group(1)
                time_index = index
            if stripped.casefold() == RESPONSE_MARKER:
                response_index = index
                break

        user_start = (time_index + 1) if time_index is not None else (start + 1)
        user_end = response_index if response_index is not None else end
        response_start = (response_index + 1) if response_index is not None else end

        blocks.append(
            ConversationBlock(
                index=len(blocks),
                start_line=start + 1,
                end_line=end,
                time=time_value,
                user_message="".join(lines[user_start:user_end]).strip(),
                gemini_response="".join(lines[response_start:end]).strip(),
                raw="".join(lines[start:end]).strip() + "\n",
            )
        )

    return blocks


def find_old_boundary(old_blocks: list[ConversationBlock]) -> ConversationBlock:
    if not old_blocks:
        raise ValueError("The old history does not contain a 'you asked' block.")
    timed_blocks = [block for block in old_blocks if block.time]
    return timed_blocks[-1] if timed_blocks else old_blocks[-1]


def find_new_boundary(
    old_boundary: ConversationBlock, new_blocks: list[ConversationBlock]
) -> tuple[int, str, float | None]:
    if not new_blocks:
        raise ValueError("The new history does not contain a 'you asked' block.")

    if old_boundary.time:
        matches = [
            index
            for index, block in enumerate(new_blocks)
            if block.time == old_boundary.time
        ]
        if matches:
            return matches[-1], "timestamp", 1.0

    normalized_old = normalize_message(old_boundary.user_message)
    exact_matches = [
        index
        for index, block in enumerate(new_blocks)
        if normalize_message(block.user_message) == normalized_old
    ]
    if exact_matches:
        return exact_matches[-1], "normalized-message", 1.0

    best_index: int | None = None
    best_ratio = 0.0
    for index, block in enumerate(new_blocks):
        ratio = difflib.SequenceMatcher(
            None, normalized_old, normalize_message(block.user_message)
        ).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_index = index

    if best_index is not None and best_ratio >= 0.86:
        return best_index, "similar-message", best_ratio

    if old_boundary.time:
        for index, block in enumerate(new_blocks):
            if block.time and block.time > old_boundary.time:
                return index - 1, "timestamp-fallback", None

    raise ValueError(
        "Could not locate the old boundary in the new history. "
        "Check that the files belong to the same conversation or provide contiguous exports."
    )


def build_result(
    old_path: Path,
    new_path: Path,
    boundary: ConversationBlock,
    strategy: str,
    confidence: float | None,
    delta: list[ConversationBlock],
) -> dict:
    return {
        "old_file": str(old_path),
        "new_file": str(new_path),
        "old_boundary": {
            "time": boundary.time,
            "line": boundary.start_line,
            "user_message": boundary.user_message,
        },
        "match_strategy": strategy,
        "match_confidence": confidence,
        "new_block_count": len(delta),
        "new_blocks": [asdict(block) for block in delta],
    }


def render_text(result: dict) -> str:
    boundary = result["old_boundary"]
    header = [
        f"Old boundary: {boundary['time'] or 'no timestamp'} (line {boundary['line']})",
        f"Boundary strategy: {result['match_strategy']}",
        f"New blocks: {result['new_block_count']}",
        "",
    ]
    body = [block["raw"].rstrip() for block in result["new_blocks"]]
    return "\n".join(header) + "\n\n".join(body) + ("\n" if body else "")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract new Gemini conversation blocks from a cumulative history export."
    )
    parser.add_argument("old_history", type=Path)
    parser.add_argument("new_history", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        old_text = args.old_history.read_text(encoding="utf-8")
        new_text = args.new_history.read_text(encoding="utf-8")
        old_blocks = parse_blocks(old_text)
        new_blocks = parse_blocks(new_text)
        old_boundary = find_old_boundary(old_blocks)
        boundary_index, strategy, confidence = find_new_boundary(
            old_boundary, new_blocks
        )
        delta = new_blocks[boundary_index + 1 :]
        result = build_result(
            args.old_history,
            args.new_history,
            old_boundary,
            strategy,
            confidence,
            delta,
        )
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    rendered = (
        json.dumps(result, ensure_ascii=False, indent=2)
        if args.format == "json"
        else render_text(result)
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
