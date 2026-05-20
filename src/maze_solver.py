from __future__ import annotations

import ast
import json
from collections import deque
from typing import Iterable


Coord = tuple[int, int]


WALL_CHARS = {"#", "1", "X", "x", "W", "w", "@"}
START_CHARS = {"S", "s", "A", "a"}
END_CHARS = {"E", "e", "G", "g", "T", "t", "F", "f"}


def parse_coord(value: object) -> Coord | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return int(value[0]), int(value[1])
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, (list, tuple)) and len(parsed) == 2:
            return int(parsed[0]), int(parsed[1])
    except (SyntaxError, ValueError):
        pass

    parts = text.replace("(", "").replace(")", "").replace("[", "").replace("]", "").split(",")
    if len(parts) == 2:
        return int(parts[0].strip()), int(parts[1].strip())
    return None


def parse_grid(value: object) -> list[list[str]]:
    if value is None:
        raise ValueError("maze value is empty")

    if isinstance(value, list):
        rows = value
    else:
        text = str(value).strip()
        if not text or text.lower() == "nan":
            raise ValueError("maze value is empty")
        rows = _parse_serialized_grid(text)

    grid: list[list[str]] = []
    for row in rows:
        if isinstance(row, str):
            grid.append(list(row))
        else:
            grid.append([str(cell) for cell in row])
    if not grid:
        raise ValueError("maze grid has no rows")
    return grid


def _parse_serialized_grid(text: str) -> list[object]:
    for parser in (json.loads, ast.literal_eval):
        try:
            parsed = parser(text)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, SyntaxError, ValueError):
            pass

    if "\\n" in text:
        text = text.replace("\\n", "\n")
    if "\n" in text:
        return [line for line in text.splitlines() if line]
    if "|" in text:
        return [line for line in text.split("|") if line]
    if ";" in text:
        return [line for line in text.split(";") if line]

    raise ValueError("unsupported maze grid encoding")


def find_marker(grid: list[list[str]], markers: set[str]) -> Coord | None:
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell in markers:
                return r, c
    return None


def solve_maze(
    grid: list[list[str]],
    start: Coord | None = None,
    end: Coord | None = None,
) -> str:
    start = start or find_marker(grid, START_CHARS)
    end = end or find_marker(grid, END_CHARS)

    if start is None:
        start = _first_open_cell(grid)
    if end is None:
        end = _last_open_cell(grid)
    if start is None or end is None:
        return ""

    parents: dict[Coord, tuple[Coord, str]] = {}
    queue: deque[Coord] = deque([start])
    seen = {start}

    moves = [
        (-1, 0, "U"),
        (1, 0, "D"),
        (0, -1, "L"),
        (0, 1, "R"),
    ]

    while queue:
        current = queue.popleft()
        if current == end:
            return _reconstruct_path(parents, start, end)

        for dr, dc, move in moves:
            nxt = current[0] + dr, current[1] + dc
            if nxt in seen or not _is_open(grid, nxt):
                continue
            seen.add(nxt)
            parents[nxt] = current, move
            queue.append(nxt)

    return ""


def _is_open(grid: list[list[str]], coord: Coord) -> bool:
    r, c = coord
    if r < 0 or r >= len(grid):
        return False
    if c < 0 or c >= len(grid[r]):
        return False
    return grid[r][c] not in WALL_CHARS


def _open_cells(grid: list[list[str]]) -> Iterable[Coord]:
    for r, row in enumerate(grid):
        for c, _ in enumerate(row):
            if _is_open(grid, (r, c)):
                yield r, c


def _first_open_cell(grid: list[list[str]]) -> Coord | None:
    return next(iter(_open_cells(grid)), None)


def _last_open_cell(grid: list[list[str]]) -> Coord | None:
    last = None
    for coord in _open_cells(grid):
        last = coord
    return last


def _reconstruct_path(parents: dict[Coord, tuple[Coord, str]], start: Coord, end: Coord) -> str:
    moves: list[str] = []
    current = end
    while current != start:
        parent, move = parents[current]
        moves.append(move)
        current = parent
    return "".join(reversed(moves))
