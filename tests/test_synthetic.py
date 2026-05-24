from ecog_cortical_speech_decoder.synthetic import run_decoder_smoke_test


def test_synthetic_decoder_beats_chance():
    metrics = run_decoder_smoke_test(random_state=11)

    assert metrics["accuracy"] > 0.8
    assert metrics["chance"] == 0.5
