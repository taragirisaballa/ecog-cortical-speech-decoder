from ecog_cortical_speech_decoder.dandi import DandiAsset, format_bytes, parse_session, parse_subject, summarize_assets


def test_parse_subject_and_session_from_asset_path():
    path = "sub-EC2/sub-EC2_ses-EC2-B76.nwb"

    assert parse_subject(path) == "EC2"
    assert parse_session(path) == "EC2-B76"


def test_summarize_assets_counts_sessions_and_size():
    assets = [
        DandiAsset("a", "sub-EC2/sub-EC2_ses-EC2-B76.nwb", 1024, "", "", "EC2", "EC2-B76"),
        DandiAsset("b", "sub-EC2/sub-EC2_ses-EC2-B105.nwb", 2048, "", "", "EC2", "EC2-B105"),
        DandiAsset("c", "sub-EC3/sub-EC3_ses-EC3-B1.nwb", 4096, "", "", "EC3", "EC3-B1"),
    ]

    summary = summarize_assets(assets)

    assert summary.asset_count == 3
    assert summary.total_size_bytes == 7168
    assert summary.subjects == ("EC2", "EC3")
    assert summary.sessions_by_subject == {"EC2": 2, "EC3": 1}
    assert summary.largest_asset is assets[2]


def test_format_bytes_uses_binary_units():
    assert format_bytes(1024) == "1.0 KiB"
