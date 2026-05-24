from ecog_cortical_speech_decoder.dandi import DandisetSummary
from ecog_cortical_speech_decoder.report import render_dataset_card


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
