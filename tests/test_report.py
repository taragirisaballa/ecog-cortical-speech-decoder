from ecog_cortical_speech_decoder.dandi import DandiAsset, DandisetSummary
from ecog_cortical_speech_decoder.report import render_asset_inventory, render_asset_inventory_csv, render_dataset_card


def test_render_dataset_card_includes_dataset_fields():
    summary = DandisetSummary(
        dandiset_id="000019",
        version="0.220126.2148",
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
        description="High-density ECoG speech dataset.",
        url="https://dandiarchive.org/dandiset/000019/0.220126.2148",
    )

    card = render_dataset_card(summary)

    assert "consonant-vowel" in card
    assert "high-gamma" in card
    assert "Neurodata Without Borders" in card
    assert "000019" in card


def test_render_asset_inventory_outputs_real_asset_fields():
    assets = [
        DandiAsset(
            asset_id="aff7ccb8",
            path="sub-EC2/sub-EC2_ses-EC2-B76.nwb",
            size_bytes=1862205526,
            created="2021-07-02T13:28:08Z",
            modified="2021-08-05T18:46:45Z",
            subject="EC2",
            session="EC2-B76",
        )
    ]

    markdown = render_asset_inventory(assets, "000019", "0.220126.2148")
    csv_text = render_asset_inventory_csv(assets)

    assert "Asset Inventory" in markdown
    assert "sub-EC2_ses-EC2-B76.nwb" in markdown
    assert "EC2-B76" in csv_text
    assert "size_bytes" in csv_text
