import numpy as np
import pytest

from b2b.beatgrid import local_attack_offset, rhythm


def house_pulses(bpm=125., offset=.137, duration=48., start=0., sr=22050):
    """Known broadband drum attacks with a deliberately delayed low-frequency body."""
    y = np.zeros(round(duration * sr))
    rng = np.random.default_rng(51)
    attack_t = np.arange(round(.025 * sr)) / sr
    click = .7 * rng.normal(size=len(attack_t)) * np.exp(-attack_t / .003)
    bass_t = np.arange(round(.16 * sr)) / sr
    bass = np.sin(2 * np.pi * 62 * bass_t) * np.exp(-bass_t / .06)
    for beat in np.arange(offset, duration - .2, 60 / bpm):
        if beat < start:
            continue
        at = round(beat * sr)
        y[at:at + len(click)] += click
        at += round(.030 * sr)
        y[at:at + len(bass)] += bass
    return y


def test_grid_anchors_attack_despite_delayed_bass_and_drumless_opening():
    y = house_pulses(start=8.)
    bpm, phase, beats, confidence, kicks, envelope = rhythm(y)
    assert abs(bpm - 125) < .025
    assert abs(phase - .137) < .010
    assert confidence > .8
    assert len(beats) > 90


def test_local_rendered_offset_sign_and_precision():
    # A +32ms rendered delay needs +32ms in the prepared-file seek position.
    y = house_pulses(offset=.137 + .032)
    result = local_attack_offset(y, 22050, 125., .137, 12., 28.)
    assert result['reliable']
    assert result['offset'] == pytest.approx(.032, abs=.005)
    assert result['spread'] < .005


def test_empty_or_too_sparse_window_never_claims_alignment():
    silent = np.zeros(22050 * 20)
    result = local_attack_offset(silent, 22050, 125., .137)
    assert result['offset'] == 0.
    assert not result['reliable']
    y = house_pulses(start=18.)
    result = local_attack_offset(y, 22050, 125., .137, 12., 20.)
    assert not result['reliable']
