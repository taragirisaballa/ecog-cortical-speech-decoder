"""Markdown reports for dataset notes."""

from __future__ import annotations

from .dandi import DandisetSummary


def render_dataset_card(summary: DandisetSummary) -> str:
    """Render a concise dataset note."""

    contributors = ", ".join(summary.contributors) or "Not listed"
    keywords = ", ".join(summary.keywords) or "Not listed"
    file_count = "Unknown" if summary.file_count is None else str(summary.file_count)
    subject_count = "Unknown" if summary.subject_count is None else str(summary.subject_count)

    return f"""# Dataset Notes: {summary.name}

DANDI `{summary.dandiset_id}` contains human ECoG recordings collected during consonant-vowel syllable production. This dataset is useful for practicing NWB inspection, ECoG preprocessing, high-gamma feature extraction, and simple speech-decoding baselines.

## Snapshot

| Field | Value |
| --- | --- |
| DANDI ID | `{summary.dandiset_id}` |
| Version | `{summary.version}` |
| DOI | `{summary.doi}` |
| License | `{summary.license}` |
| Files | {file_count} |
| Size | {summary.size} |
| Species | {summary.species} |
| Subjects | {subject_count} |
| Approach | {summary.approach} |
| Data standard | {summary.data_standard} |
| Keywords | {keywords} |
| Contributors | {contributors} |

## Questions To Explore

1. How much syllable information is recoverable from high-gamma ECoG features?
2. Which channels carry the most consonant-vowel discriminative signal?
3. Do interpretable linear models and nonlinear models disagree about cortical feature importance?
4. Can a compact decoder produce stable performance across subjects or sessions?

Dataset URL: {summary.url}
"""
