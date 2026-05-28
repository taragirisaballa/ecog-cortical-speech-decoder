"""Small DANDI API client for public dandiset metadata."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
import subprocess
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_DANDISET_ID = "000019"
DEFAULT_VERSION = "0.220126.2148"
API_BASE = "https://api.dandiarchive.org/api"


def built_in_summary() -> "DandisetSummary":
    """Return a small checked metadata snapshot for offline demos."""

    return DandisetSummary(
        dandiset_id=DEFAULT_DANDISET_ID,
        version=DEFAULT_VERSION,
        name="Human ECoG speaking consonant-vowel syllables",
        doi="10.48324/dandi.000019/0.220126.2148",
        license="spdx:CC-BY-4.0",
        size="51.8 GiB",
        file_count=31,
        species="Human",
        approach="electrophysiological approach",
        data_standard="Neurodata Without Borders (NWB)",
        subject_count=4,
        keywords=("electrocorticography (ECoG)", "speech production"),
        contributors=("Bouchard, Kristofer E.", "Chang, Edward F."),
        description=(
            "High-density ECoG recordings from participants producing consonant-vowel "
            "syllables."
        ),
        url=f"https://dandiarchive.org/dandiset/{DEFAULT_DANDISET_ID}/{DEFAULT_VERSION}",
    )


@dataclass(frozen=True)
class DandisetSummary:
    """Compact summary of a DANDI dandiset."""

    dandiset_id: str
    version: str
    name: str
    doi: str
    license: str
    size: str
    file_count: int | None
    species: str
    approach: str
    data_standard: str
    subject_count: int | None
    keywords: tuple[str, ...]
    contributors: tuple[str, ...]
    description: str
    url: str

    @classmethod
    def from_dandi_payload(
        cls, payload: dict[str, Any], dandiset_id: str, version: str
    ) -> "DandisetSummary":
        """Normalize DANDI's nested metadata into a compact summary."""

        metadata = payload.get("metadata", payload)
        assets_summary = metadata.get("assetsSummary", {}) or {}
        contributors = tuple(
            item.get("name", "")
            for item in metadata.get("contributor", [])
            if isinstance(item, dict) and item.get("name")
        )
        keywords = tuple(str(keyword) for keyword in metadata.get("keywords", []) or [])
        license_value = metadata.get("license", "")
        if isinstance(license_value, list):
            license_value = ", ".join(str(value) for value in license_value)

        return cls(
            dandiset_id=dandiset_id,
            version=version,
            name=str(metadata.get("name", "Unknown dandiset")),
            doi=str(metadata.get("doi", "")),
            license=str(license_value),
            size=str(assets_summary.get("numberOfBytes", "")),
            file_count=assets_summary.get("numberOfFiles"),
            species=_first_name(assets_summary.get("species")),
            approach=_first_name(assets_summary.get("approach")),
            data_standard=_first_name(assets_summary.get("dataStandard")),
            subject_count=assets_summary.get("numberOfSubjects"),
            keywords=keywords,
            contributors=contributors,
            description=str(metadata.get("description", "")).strip(),
            url=f"https://dandiarchive.org/dandiset/{dandiset_id}/{version}",
        )


@dataclass(frozen=True)
class DandiAsset:
    """One file-like asset listed by a DANDI dandiset version."""

    asset_id: str
    path: str
    size_bytes: int
    created: str
    modified: str
    subject: str
    session: str

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "DandiAsset":
        path = str(payload.get("path", ""))
        return cls(
            asset_id=str(payload.get("asset_id", "")),
            path=path,
            size_bytes=int(payload.get("size") or 0),
            created=str(payload.get("created", "")),
            modified=str(payload.get("modified", "")),
            subject=parse_subject(path),
            session=parse_session(path),
        )


@dataclass(frozen=True)
class AssetInventorySummary:
    """Summary statistics for the listed DANDI assets."""

    asset_count: int
    total_size_bytes: int
    subjects: tuple[str, ...]
    sessions_by_subject: dict[str, int]
    largest_asset: DandiAsset | None


def fetch_json(url: str, timeout: int = 30) -> dict[str, Any]:
    """Fetch JSON from a public API endpoint."""

    request = Request(url, headers={"Accept": "application/json", "User-Agent": "ecog-decoder/0.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        return _fetch_json_with_curl(url, exc)


def fetch_dandiset_summary(
    dandiset_id: str = DEFAULT_DANDISET_ID, version: str = DEFAULT_VERSION
) -> DandisetSummary:
    """Fetch published DANDI metadata for a dandiset."""

    url = f"{API_BASE}/dandisets/{dandiset_id}/versions/{version}/"
    return DandisetSummary.from_dandi_payload(fetch_json(url), dandiset_id, version)


def fetch_asset_page(
    dandiset_id: str = DEFAULT_DANDISET_ID,
    version: str = DEFAULT_VERSION,
    page_size: int = 25,
) -> dict[str, Any]:
    """Fetch one page of asset metadata without downloading NWB files."""

    url = f"{API_BASE}/dandisets/{dandiset_id}/versions/{version}/assets/?page_size={page_size}"
    return fetch_json(url)


def fetch_assets(
    dandiset_id: str = DEFAULT_DANDISET_ID,
    version: str = DEFAULT_VERSION,
    page_size: int = 100,
) -> list[DandiAsset]:
    """Fetch all asset records for a dandiset version without downloading data files."""

    url: str | None = (
        f"{API_BASE}/dandisets/{dandiset_id}/versions/{version}/assets/?page_size={page_size}"
    )
    assets: list[DandiAsset] = []
    while url:
        payload = fetch_json(url)
        assets.extend(DandiAsset.from_payload(item) for item in payload.get("results", []))
        url = payload.get("next")
    return assets


def summarize_assets(assets: list[DandiAsset]) -> AssetInventorySummary:
    """Summarize asset counts, size, subjects, and sessions."""

    subjects = tuple(sorted({asset.subject for asset in assets if asset.subject}))
    sessions_by_subject = {
        subject: len({asset.session for asset in assets if asset.subject == subject and asset.session})
        for subject in subjects
    }
    largest_asset = max(assets, key=lambda asset: asset.size_bytes, default=None)
    return AssetInventorySummary(
        asset_count=len(assets),
        total_size_bytes=sum(asset.size_bytes for asset in assets),
        subjects=subjects,
        sessions_by_subject=sessions_by_subject,
        largest_asset=largest_asset,
    )


def parse_subject(path: str) -> str:
    """Extract the BIDS-like subject label from a DANDI asset path."""

    first_part = path.split("/", maxsplit=1)[0]
    return first_part.removeprefix("sub-") if first_part.startswith("sub-") else ""


def parse_session(path: str) -> str:
    """Extract the session label from a DANDI asset path."""

    match = re.search(r"_ses-([^_/.]+)", path)
    return match.group(1) if match else ""


def format_bytes(size_bytes: int) -> str:
    """Format bytes using binary units."""

    value = float(size_bytes)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} TiB"


def _first_name(value: Any) -> str:
    if isinstance(value, list) and value:
        value = value[0]
    if isinstance(value, dict):
        return str(value.get("name", value.get("identifier", "")))
    return str(value or "")


def _fetch_json_with_curl(url: str, original_error: BaseException) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["curl", "-sS", url],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.SubprocessError, FileNotFoundError) as exc:
        raise RuntimeError(f"Could not fetch {url}: {original_error}") from exc
    return json.loads(result.stdout)
