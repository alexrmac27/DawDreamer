import os

import numpy as np
import pytest
from scipy.io import wavfile

import dawdreamer as daw

SAMPLE_RATE = 44100
BUFFER_SIZE = 512


def _coldpiano_vst3_path():
    vst3_path = os.environ.get("COLDPIANO_VST3_PATH")
    if vst3_path is None:
        pytest.skip("Set COLDPIANO_VST3_PATH to run the Coldpiano integration test")
    assert os.path.exists(vst3_path), f"Missing VST3 at {vst3_path}"
    return vst3_path


def test_coldpiano_path_unset(monkeypatch):
    monkeypatch.delenv("COLDPIANO_VST3_PATH", raising=False)
    with pytest.raises(pytest.skip.Exception):
        _coldpiano_vst3_path()


def test_coldpiano_path_missing(monkeypatch, tmp_path):
    missing_path = tmp_path / "missing.vst3"
    monkeypatch.setenv("COLDPIANO_VST3_PATH", str(missing_path))
    with pytest.raises(AssertionError, match="Missing VST3"):
        _coldpiano_vst3_path()


def test_coldpiano_path_present(monkeypatch, tmp_path):
    vst3_path = tmp_path / "Coldpiano.vst3"
    vst3_path.mkdir()
    monkeypatch.setenv("COLDPIANO_VST3_PATH", str(vst3_path))
    assert _coldpiano_vst3_path() == str(vst3_path)


def test_coldpiano_renders_chord_progression():
    vst3_path = _coldpiano_vst3_path()
    engine = daw.RenderEngine(SAMPLE_RATE, BUFFER_SIZE)
    coldpiano = engine.make_plugin_processor("coldpiano", vst3_path)

    notes = [
        (48, 95, 0.1, 2.5),
        (55, 85, 0.3, 2.3),
        (62, 90, 0.5, 2.1),
        (63, 100, 0.7, 1.9),
        (67, 88, 0.9, 1.7),
    ]
    for pitch, velocity, start, duration in notes:
        coldpiano.add_midi_note(pitch, velocity, start, duration)

    engine.load_graph([(coldpiano, [])])
    assert engine.render(3.5)

    audio = engine.get_audio()
    assert audio.shape == (2, int(SAMPLE_RATE * 3.5))
    assert np.all(np.isfinite(audio)), "NaN or Inf detected in Coldpiano output!"

    peak = float(np.max(np.abs(audio)))
    print(f"Rendered Coldpiano audio peak amplitude: {peak:.5f}")
    assert peak > 1e-4, "Rendered audio is silent!"

    out_wav = os.path.join(os.path.dirname(__file__), "coldpiano_test_render.wav")
    wavfile.write(out_wav, SAMPLE_RATE, audio.T.astype(np.float32))
