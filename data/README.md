# Data

This directory is for Kaggle competition data and derived datasets.

## Folders

- `raw/` - downloaded competition files from Kaggle.
- `processed/` - cleaned, feature-engineered, or derived files.

Raw and processed data are ignored by git because Kaggle competition data may be private, large, or governed by competition-specific rules. Keep only lightweight placeholders and documentation in GitHub unless the competition rules explicitly allow redistribution.

## Download

From the project root:

```powershell
python src\download_data.py
```

If download fails, check that:

- You accepted the competition rules on Kaggle.
- Your Kaggle credentials are configured locally.
- The `kaggle` package is installed in your active environment.
