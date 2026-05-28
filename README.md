# ECoG Cortical Speech Decoder

Exploratory code for working with open human ECoG speech data. The current focus is DANDI `000019`, a 256-channel ECoG dataset collected during consonant-vowel syllable production.

The repository currently works with public DANDI metadata, writes an asset inventory for the NWB files, and includes a synthetic ECoG decoding example for testing the feature/decoder code. Raw NWB files are not included because the dataset is large.

## Dataset

- DANDI: `000019`
- Title: Human ECoG speaking consonant-vowel syllables
- Standard: Neurodata Without Borders (NWB)
- License: CC-BY-4.0
- Approximate size: 51.8 GiB
- Subjects: 4

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,neuro]"
```

## Commands

Generate local dataset notes from the checked metadata snapshot:

```bash
ecog-cortical-speech-decoder dataset-card --offline
```

Fetch the live DANDI asset list and write `reports/asset_inventory.md` plus `reports/asset_inventory.csv`:

```bash
ecog-cortical-speech-decoder asset-inventory
```

Run the synthetic decoder example:

```bash
ecog-cortical-speech-decoder smoke-decode
```

Run tests:

```bash
pytest
```

## Project Layout

```text
src/ecog_cortical_speech_decoder/   Python package and CLI
tests/                              Unit tests
reports/                            Dataset notes, asset inventory, and future figures
data/raw/                           Local raw NWB files, ignored by git
data/processed/                     Local derived features, ignored by git
```

## Next Steps

- Inspect one downloaded NWB file and summarize the available streams, electrodes, and labels.
- Use the asset inventory to choose a first small session to download.
- Extract trial-aligned high-gamma features.
- Train a simple baseline decoder for syllable labels.
- Compare performance across channels and time windows.

## References

- Sumner Norman, Open Source Data: https://sumnernorman.com/open-source-data
- DANDI `000019`: https://dandiarchive.org/dandiset/000019/0.220126.2148
- Livezey, Bouchard, and Chang, 2019: https://doi.org/10.1371/journal.pcbi.1007091
