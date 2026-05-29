"""Session selection helpers for DANDI ECoG assets."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from .dandi import API_BASE, DandiAsset, format_bytes


@dataclass(frozen=True)
class SessionPlan:
    """A selected NWB asset and the rule used to choose it."""

    dandiset_id: str
    version: str
    asset: DandiAsset
    selection_rule: str
    download_url: str
    local_path: str


def select_session_asset(
    assets: list[DandiAsset],
    *,
    subject: str | None = None,
    strategy: str = "smallest",
) -> DandiAsset:
    """Select one asset for the first local NWB inspection pass."""

    candidates = [asset for asset in assets if subject is None or asset.subject == subject]
    if not candidates:
        raise ValueError("No DANDI assets match the requested filters.")
    if strategy != "smallest":
        raise ValueError(f"Unsupported selection strategy: {strategy}")
    return min(candidates, key=lambda asset: (asset.size_bytes, asset.path))


def build_session_plan(
    assets: list[DandiAsset],
    dandiset_id: str,
    version: str,
    *,
    subject: str | None = None,
    strategy: str = "smallest",
    raw_dir: str = "data/raw",
) -> SessionPlan:
    """Build a manifest for the selected DANDI asset."""

    asset = select_session_asset(assets, subject=subject, strategy=strategy)
    local_path = str(Path(raw_dir) / asset.path)
    return SessionPlan(
        dandiset_id=dandiset_id,
        version=version,
        asset=asset,
        selection_rule=_selection_rule(strategy, subject),
        download_url=f"{API_BASE}/assets/{asset.asset_id}/download/",
        local_path=local_path,
    )


def render_session_plan(plan: SessionPlan, assets: list[DandiAsset], limit: int = 8) -> str:
    """Render the selected session and nearby candidate assets as Markdown."""

    candidates = sorted(assets, key=lambda asset: (asset.size_bytes, asset.path))[:limit]
    candidate_rows = "\n".join(
        f"| `{asset.path}` | {asset.subject} | {asset.session} | {format_bytes(asset.size_bytes)} |"
        for asset in candidates
    )
    return f"""# Session Plan: DANDI {plan.dandiset_id}

This plan selects one NWB file for the first local inspection pass. The selected file is small enough to download before working through the larger sessions.

## Selected Asset

| Field | Value |
| --- | --- |
| DANDI version | `{plan.version}` |
| Selection rule | {plan.selection_rule} |
| Path | `{plan.asset.path}` |
| Subject | {plan.asset.subject} |
| Session | {plan.asset.session} |
| Size | {format_bytes(plan.asset.size_bytes)} |
| Asset ID | `{plan.asset.asset_id}` |
| Download endpoint | `{plan.download_url}` |
| Local path | `{plan.local_path}` |

## Smallest Candidate Assets

| Path | Subject | Session | Size |
| --- | --- | --- | ---: |
{candidate_rows}

## Inspection Checklist

- Open the NWB file without loading full data arrays into memory.
- List acquisition objects, processing modules, intervals, and electrode metadata.
- Identify trial labels and timing fields needed for syllable decoding.
- Save a short inspection report before extracting high-gamma features.
"""


def render_session_manifest(plan: SessionPlan) -> str:
    """Render the selected session as machine-readable JSON."""

    payload = {
        "dandiset_id": plan.dandiset_id,
        "version": plan.version,
        "selection_rule": plan.selection_rule,
        "asset": {
            "asset_id": plan.asset.asset_id,
            "path": plan.asset.path,
            "subject": plan.asset.subject,
            "session": plan.asset.session,
            "size_bytes": plan.asset.size_bytes,
            "size": format_bytes(plan.asset.size_bytes),
            "created": plan.asset.created,
            "modified": plan.asset.modified,
        },
        "download_url": plan.download_url,
        "local_path": plan.local_path,
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _selection_rule(strategy: str, subject: str | None) -> str:
    if subject:
        return f"{strategy} asset for subject {subject}"
    return f"{strategy} asset overall"
