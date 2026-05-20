# Maze Crawler Kaggle Project

Workspace for the Kaggle competition: https://www.kaggle.com/competitions/maze-crawler

## Current Status

The repository is scaffolded for exploration, local data download, baseline development, and Kaggle submissions.

Kaggle's public web page is rendered dynamically, so the full competition overview/data/evaluation text may require authenticated access in a browser or through the Kaggle API. Raw competition files should not be committed unless the competition rules explicitly allow redistribution.

## Project Layout

```text
data/
  raw/          # local-only competition downloads
  processed/    # local-only cleaned or derived data
notebooks/      # exploratory notebooks
src/            # reusable Python code
submissions/    # generated submission files
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Download Competition Data

Use the Kaggle competition page to accept the rules first if required:

https://www.kaggle.com/competitions/maze-crawler

Then use one of the supported Kaggle authentication methods. Do not commit credentials.

For the standard Kaggle CLI, place `kaggle.json` at:

```text
C:\Users\<you>\.kaggle\kaggle.json
```

Then run:

```powershell
python src\download_data.py
```

Downloaded files will go under `data/raw/` and remain ignored by git.

## Next Steps

1. Inspect competition files and evaluation metric.
2. Add an exploratory notebook for the train/test/schema overview.
3. Build a deterministic baseline submission.
4. Iterate with stronger pathfinding/modeling strategies based on the actual data format.
