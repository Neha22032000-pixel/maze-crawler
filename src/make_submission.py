from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from maze_solver import parse_coord, parse_grid, solve_maze


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "raw"
DEFAULT_OUTPUT = PROJECT_ROOT / "submissions" / "baseline_submission.csv"


ID_CANDIDATES = {"id", "ID", "Id", "row_id", "RowId", "rowId"}
MAZE_CANDIDATES = ("maze", "grid", "map", "board", "input")
START_CANDIDATES = ("start", "source", "begin")
END_CANDIDATES = ("end", "target", "goal", "finish")
PATH_CANDIDATES = ("path", "moves", "solution", "actions", "answer")


def main() -> None:
    args = parse_args()
    data_dir = Path(args.data_dir)
    output_path = Path(args.output)

    sample_path = find_file(data_dir, "sample_submission.csv")
    test_path = find_file(data_dir, "test.csv")

    if sample_path is None:
        raise FileNotFoundError(
            f"Could not find sample_submission.csv under {data_dir}. "
            "Download the Kaggle competition files first."
        )

    sample = pd.read_csv(sample_path)
    test = pd.read_csv(test_path) if test_path else pd.DataFrame()
    submission = build_submission(sample, test)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    submission.to_csv(output_path, index=False)
    print(f"Wrote {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a baseline Kaggle submission.")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR, help="Directory containing Kaggle CSV files.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Submission CSV path.")
    return parser.parse_args()


def find_file(root: Path, filename: str) -> Path | None:
    matches = sorted(root.rglob(filename))
    return matches[0] if matches else None


def build_submission(sample: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    submission = sample.copy()
    id_cols = [col for col in submission.columns if col in ID_CANDIDATES]
    target_cols = [col for col in submission.columns if col not in id_cols]

    if test.empty or not target_cols:
        return fill_fallback(submission, target_cols)

    path_col = choose_column(target_cols, PATH_CANDIDATES) or target_cols[0]
    maze_col = choose_column(test.columns, MAZE_CANDIDATES)

    if maze_col is None:
        return fill_fallback(submission, target_cols)

    start_col = choose_column(test.columns, START_CANDIDATES)
    end_col = choose_column(test.columns, END_CANDIDATES)

    paths = []
    for _, row in test.iterrows():
        try:
            grid = parse_grid(row[maze_col])
            start = parse_coord(row[start_col]) if start_col else None
            end = parse_coord(row[end_col]) if end_col else None
            paths.append(solve_maze(grid, start=start, end=end))
        except Exception:
            paths.append("")

    if len(paths) == len(submission):
        submission[path_col] = paths
        for col in target_cols:
            if col != path_col:
                submission[col] = fallback_value(submission[col])
        return submission

    return fill_fallback(submission, target_cols)


def choose_column(columns: object, candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        for col in columns:
            if str(col).lower() == candidate.lower():
                return str(col)
    for candidate in candidates:
        for col in columns:
            if candidate.lower() in str(col).lower():
                return str(col)
    return None


def fill_fallback(submission: pd.DataFrame, target_cols: list[str]) -> pd.DataFrame:
    for col in target_cols:
        submission[col] = fallback_value(submission[col])
    return submission


def fallback_value(series: pd.Series) -> object:
    non_null = series.dropna()
    if not non_null.empty:
        return non_null.iloc[0]
    if pd.api.types.is_numeric_dtype(series):
        return 0
    return ""


if __name__ == "__main__":
    main()
