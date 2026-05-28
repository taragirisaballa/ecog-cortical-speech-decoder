"""Markdown reports for dataset notes."""

from __future__ import annotations

import csv
from io import StringIO

from .dandi import DandiAsset, DandisetSummary, format_bytes, summarize_assets


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

1. What fields and labels are available in the NWB files?
2. How should trials be aligned for consonant-vowel production?
3. How much information is present in high-gamma power features?
4. Which channels and time windows are most useful for a baseline decoder?

Dataset URL: {summary.url}
"""


def render_asset_inventory(assets: list[DandiAsset], dandiset_id: str, version: str) -> str:
    """Render a Markdown report from real DANDI asset records."""

    summary = summarize_assets(assets)
    subject_rows = "\n".join(
        f"| {subject} | {summary.sessions_by_subject[subject]} |"
        for subject in summary.subjects
    )
    largest = summary.largest_asset
    largest_text = "None"
    if largest is not None:
        largest_text = f"`{largest.path}` ({format_bytes(largest.size_bytes)})"

    asset_rows = "\n".join(
        f"| `{asset.path}` | {asset.subject} | {asset.session} | {format_bytes(asset.size_bytes)} |"
        for asset in sorted(assets, key=lambda item: item.path)
    )

    return f"""# Asset Inventory: DANDI {dandiset_id}

This report lists the NWB assets exposed by the DANDI API for version `{version}`. It uses metadata only; no raw neural recordings are downloaded.

## Summary

| Field | Value |
| --- | --- |
| Assets | {summary.asset_count} |
| Total listed size | {format_bytes(summary.total_size_bytes)} |
| Subjects | {len(summary.subjects)} |
| Largest asset | {largest_text} |

## Sessions By Subject

| Subject | Sessions |
| --- | ---: |
{subject_rows}

## Assets

| Path | Subject | Session | Size |
| --- | --- | --- | ---: |
{asset_rows}
"""


def render_asset_inventory_csv(assets: list[DandiAsset]) -> str:
    """Render asset records as CSV text."""

    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["path", "subject", "session", "size_bytes", "size", "asset_id", "created", "modified"],
    )
    writer.writeheader()
    for asset in sorted(assets, key=lambda item: item.path):
        writer.writerow(
            {
                "path": asset.path,
                "subject": asset.subject,
                "session": asset.session,
                "size_bytes": asset.size_bytes,
                "size": format_bytes(asset.size_bytes),
                "asset_id": asset.asset_id,
                "created": asset.created,
                "modified": asset.modified,
            }
        )
    return output.getvalue()
