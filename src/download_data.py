from pathlib import Path
import subprocess
import zipfile


COMPETITION = "maze-crawler"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "kaggle",
            "competitions",
            "download",
            "-c",
            COMPETITION,
            "-p",
            str(RAW_DIR),
        ],
        check=True,
    )

    for archive in RAW_DIR.glob("*.zip"):
        target = RAW_DIR / archive.stem
        target.mkdir(exist_ok=True)
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(target)
        print(f"Extracted {archive.name} -> {target}")


if __name__ == "__main__":
    main()
