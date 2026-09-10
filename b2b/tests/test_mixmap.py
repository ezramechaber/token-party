import numpy as np
from b2b.mixmap import analyze_mix_map


def fixture(kickless_bars=(), bars=40, bass=False):
    sr = 8000
    period = .5
    y = np.zeros(int(bars * 4 * period * sr))
    t = np.arange(int(.22 * sr)) / sr
    kick = np.sin(2 * np.pi * (70 * t - 35 * t ** 2)) * np.exp(-t / .065)
    kick *= np.minimum(t / .004, 1)
    for beat in range(bars * 4):
        if beat // 4 in kickless_bars:
            continue
        start = int(beat * period * sr)
        y[start:start + len(kick)] += kick
    if bass:
        y += .15 * np.sin(2 * np.pi * 55 * np.arange(len(y)) / sr)
    return y, sr


def test_kickless_first_eight_bars_yield_later_safe_entry():
    y, sr = fixture(range(8), bass=True)
    result = analyze_mix_map(y, sr, 120, 0, {'introBars': 16})
    assert result['kicklessOpening']
    assert result['firstReliableKick'] >= 15.5
    assert min(c['start'] for c in result['entryCandidates']) == 16
    assert result['strategy'] == 'choose_kick_supported_entry'


def test_gap_at_end_of_intro_is_not_a_safe_transition():
    y, sr = fixture(range(12, 16))
    result = analyze_mix_map(y, sr, 120, 0, {'introBars': 16})
    assert not result['kicklessOpening']
    assert result['introMaxKicklessBeats'] >= 16
    assert not any(c['startBar'] == 9 and c['bars'] == 8 for c in result['entryCandidates'])
    assert any(c['startBar'] == 17 and c['bars'] == 16 for c in result['entryCandidates'])


def test_sustained_bass_is_not_mistaken_for_four_on_floor_kick():
    sr = 8000
    y = .5 * np.sin(2 * np.pi * 55 * np.arange(sr * 40) / sr)
    result = analyze_mix_map(y, sr, 120, 0)
    assert result['entryCandidates'] == []
    assert result['firstReliableKick'] is None


def test_faded_tail_not_selected_as_safe_outro():
    y, sr = fixture(bars=48)
    y[32 * 2 * sr:] *= np.linspace(1, 0, len(y) - 32 * 2 * sr) ** 2
    result = analyze_mix_map(y, sr, 120, 0)
    assert result['exitCandidates']
    assert max(c['end'] for c in result['exitCandidates']) < 96


def test_map_times_are_bound_to_supplied_grid():
    y, sr = fixture()
    y = np.pad(y, (int(.125 * sr), 0))
    result = analyze_mix_map(y, sr, 120, .125)
    assert result['bars'][0]['start'] == .125
    assert result['entryCandidates'][0]['start'] == .125
    assert all(c['end'] - c['start'] == c['bars'] * 2 for c in result['entryCandidates'])


def test_human_drums_marker_overrides_early_thumps():
    y,sr=fixture()
    result=analyze_mix_map(y,sr,120,0,{'drumsIn':16,'musicIn':32})
    assert result['drumsInSource']=='human'
    assert all(row['kickState']=='absent' for row in result['bars'][:8])
    assert all(c['start']>=16 for c in result['entryCandidates'])
    assert result['musicalArrival']['time']==32
    assert result['musicalArrival']['source']=='human'


def test_musical_arrival_prefers_full_texture_over_weak_first_tones():
    from b2b.mixmap import musical_arrival
    y,sr=fixture(bars=40)
    t=np.arange(len(y))/sr
    tone=(np.sin(2*np.pi*440*t)+np.sin(2*np.pi*660*t))*.03
    y+=tone*np.where(t<8,0,np.where(t<24,1,3))
    arrival=musical_arrival(y,sr,120,0)
    assert arrival is not None
    assert arrival['time']==24
    assert arrival['confidence']=='candidate'
