import json

from ecog_cortical_speech_decoder.dandi import DandiAsset
from ecog_cortical_speech_decoder.planning import (
    build_session_plan,
    render_session_manifest,
    render_session_plan,
    select_session_asset,
)


def test_select_session_asset_picks_smallest_matching_asset():
    assets = [
        DandiAsset("a", "sub-EC2/sub-EC2_ses-EC2-B1.nwb", 2000, "", "", "EC2", "EC2-B1"),
        DandiAsset("b", "sub-EC9/sub-EC9_ses-EC9-B15.nwb", 1000, "", "", "EC9", "EC9-B15"),
        DandiAsset("c", "sub-EC9/sub-EC9_ses-EC9-B39.nwb", 3000, "", "", "EC9", "EC9-B39"),
    ]

    selected = select_session_asset(assets, subject="EC9")

    assert selected.asset_id == "b"
    assert selected.session == "EC9-B15"


def test_render_session_manifest_contains_download_target():
    asset = DandiAsset(
        "4e4287f2-b557-4f30-a2d6-932f18c3e915",
        "sub-EC9/sub-EC9_ses-EC9-B15.nwb",
        558190736,
        "2021-07-02T13:28:13Z",
        "2021-08-05T18:46:46Z",
        "EC9",
        "EC9-B15",
    )
    plan = build_session_plan([asset], "000019", "0.220126.2148")

    manifest = json.loads(render_session_manifest(plan))
    markdown = render_session_plan(plan, [asset])

    assert manifest["asset"]["path"] == "sub-EC9/sub-EC9_ses-EC9-B15.nwb"
    assert manifest["download_url"].endswith("/assets/4e4287f2-b557-4f30-a2d6-932f18c3e915/download/")
    assert "Inspection Checklist" in markdown
