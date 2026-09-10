"""Grid-bound house arrangement evidence. Kick labels are heuristics, not stems."""
import numpy as np
from scipy import signal

VERSION = 2


def _longest_gap(values):
    longest = run = 0
    for value in values:
        run = 0 if value else run + 1
        longest = max(longest, run)
    return longest


def musical_arrival(y,sr,bpm,grid_offset):
    """Propose a sustained tonal-entry boundary, not a recognized hook."""
    import librosa
    rate=min(sr,11025)
    sample=librosa.resample(np.asarray(y[:int(94*sr)],dtype=float),orig_sr=sr,target_sr=rate)
    spectrum=librosa.stft(sample,n_fft=1024,hop_length=256)
    harmonic,_=librosa.decompose.hpss(spectrum)
    frequencies=librosa.fft_frequencies(sr=rate,n_fft=1024)
    times=librosa.frames_to_time(np.arange(spectrum.shape[1]),sr=rate,hop_length=256)
    band=(frequencies>220)&(frequencies<3500)
    power=np.abs(harmonic[band])**2
    bar=240/bpm;count=int((len(sample)/rate-grid_offset)/bar)
    energy=np.asarray([np.mean(power[:,(times>=grid_offset+i*bar)&(times<grid_offset+(i+1)*bar)]) for i in range(max(0,count))])
    if len(energy)<12:return None
    reference=max(float(np.percentile(energy,75)),1e-5)
    candidates=[]
    for i in range(4,len(energy)-3,4):
        before=float(np.mean(energy[i-4:i]));after=float(np.mean(energy[i:i+4]));ratio=after/max(before,reference*.03)
        if after>reference*.5 and ratio>=2.5:
            candidates.append({'time':round(grid_offset+i*bar,4),'bar':i+1,'confidence':'candidate','source':'spectral',
                    'harmonicRise':round(ratio,2),'spectralScore':round((after-before)/reference*min(ratio,8),3),'method':'strong sustained harmonic spectral power rise over four bars','needsAudition':True})
    return max(candidates,key=lambda c:c['spectralScore']) if candidates else None


def analyze_mix_map(y, sr, bpm, grid_offset, cues=None):
    """JSON-safe kick/bass evidence and proposed 8/16-bar cue windows.

    Times are original-file seconds. Bar 1 starts at grid_offset; 4/4 is assumed.
    Confidence is heuristic evidence, not a calibrated probability. Regenerate
    after grid corrections. A bass stab can resemble a kick; musical layering,
    downbeat and arrangement meaning still need audition.
    """
    cues = cues or {}
    y = np.asarray(y, dtype=float)
    if y.ndim != 1 or len(y) < sr or sr < 1000 or not np.isfinite(y).all():
        raise ValueError('Mix maps require finite mono audio at least one second long.')
    if not np.isfinite(bpm) or bpm <= 0 or not np.isfinite(grid_offset) or grid_offset < 0:
        raise ValueError('Mix maps require a positive tempo and nonnegative grid offset.')
    duration = len(y) / sr
    period = 60 / bpm
    count = max(0, int((duration - grid_offset) / (4 * period)))
    # Five-millisecond RMS frames preserve attacks while smoothing carrier cycles.
    hop = max(1, round(sr * .005))
    low = signal.sosfiltfilt(signal.butter(3, [35, 145], fs=sr, btype='band', output='sos'), y)
    n = len(low) // hop
    env = np.sqrt(np.mean(low[:n * hop].reshape(n, hop) ** 2, axis=1))
    peaks, attacks, decays, sustain = [], [], [], []
    for beat in range(count * 4):
        t = grid_offset + beat * period
        a = env[max(0, int((t - .065) * sr / hop)):min(n, int((t + .13) * sr / hop))]
        late = env[int((t + period * .45) * sr / hop):min(n, int((t + period * .8) * sr / hop))]
        peak = float(np.max(a)) if len(a) else 0.0
        attack = max(0.0, float(np.max(np.diff(a)))) if len(a) > 1 else 0.0
        tail = float(np.mean(late)) if len(late) else 0.0
        peaks.append(peak); attacks.append(attack)
        decays.append(peak / (tail + 1e-9)); sustain.append(tail)
    peaks, attacks, decays, sustain = map(np.asarray, (peaks, attacks, decays, sustain))
    peak_ref = max(float(np.percentile(peaks, 75)) if len(peaks) else 0, 1e-5)
    attack_ref = max(float(np.percentile(attacks, 75)) if len(attacks) else 0, 1e-5)
    # Strength rejects quiet bleed/fades. Decay distinguishes a thump from bass.
    strong = ((peaks > max(peak_ref * .18, 1e-5)) &
              (attacks > max(attack_ref * .18, 1e-6)) &
              (attacks / np.maximum(peaks, 1e-9) > .045) & (decays > 1.5))
    drums_in=cues.get('drumsIn')
    if drums_in is not None:
        strong &= grid_offset+np.arange(count*4)*period>=float(drums_in)-.001
    evidence = (np.minimum(peaks / peak_ref, 1) * np.minimum(attacks / attack_ref, 1) *
                np.clip((decays - 1) / 2, 0, 1)) ** .5
    evidence = np.where(strong, evidence, 0)
    bars = []
    for i in range(count):
        part = slice(i * 4, (i + 1) * 4)
        fraction = float(np.mean(strong[part]))
        bars.append({'bar': i + 1, 'start': round(grid_offset + i * period * 4, 4),
                     'end': round(grid_offset + (i + 1) * period * 4, 4),
                     'kickFraction': round(fraction, 3),
                     'kickEvidence': round(float(np.mean(evidence[part])), 3),
                     'lowEnergy': round(float(np.mean(peaks[part])) / peak_ref, 3),
                     'sustainedLowEnergy': round(float(np.mean(sustain[part])) / peak_ref, 3),
                     'kickState': 'supported' if fraction >= .75 else 'sparse' if fraction else 'absent'})

    def candidate(start, length):
        part = slice(start * 4, (start + length) * 4)
        coverage = float(np.mean(strong[part]))
        gap = _longest_gap(strong[part])
        # A missing bar defeats a straightforward low-end handover. Both ends
        # also need support; good average coverage alone can hide a final gap.
        if coverage < .8 or gap > 2 or np.mean(strong[part][:4]) < .75 or np.mean(strong[part][-4:]) < .75:
            return None
        return {'start': round(grid_offset + start * 4 * period, 4),
                'end': round(grid_offset + (start + length) * 4 * period, 4),
                'startBar': start + 1, 'bars': length, 'kickCoverage': round(coverage, 3),
                'maxKicklessBeats': gap, 'evidence': round(float(np.mean(evidence[part])), 3),
                'confidence': 'estimated', 'needsAudition': True}

    entries, exits = [], []
    entry_limit = min(count, max(64, int(cues.get('introBars', 0)) + 16))
    exit_end = min(duration, float(cues.get('exitEnd', duration)))
    for length in (8, 16):
        for start in range(0, count - length + 1, 4):
            window = candidate(start, length)
            if not window:
                continue
            if start + length <= entry_limit:
                entries.append(window)
            if start >= max(0, count - 64) and window['end'] <= exit_end + .001:
                exits.append(window)
    arrival=({'time':float(cues['musicIn']),'confidence':'confirmed','source':'human','needsAudition':False} if cues.get('musicIn') is not None else musical_arrival(y,sr,bpm,grid_offset))
    entries.sort(key=lambda item: (abs(item['end']-arrival['time']) if arrival else item['start'], -item['bars']))
    exits.sort(key=lambda item: (-item['end'], -item['bars']))
    entries, exits = entries[:12], exits[:12]
    first_kick = next((i for i in range(max(0, len(strong) - 7))
                       if np.mean(strong[i:i + 8]) >= .875 and _longest_gap(strong[i:i + 8]) <= 1), None)
    opening_kickless = bool(len(strong) >= 8 and np.mean(strong[:8]) < .25)
    intro_end = min(count, max(0, int(cues.get('introBars', 16))))
    intro_gap = _longest_gap(strong[:intro_end * 4]) if intro_end else 0
    warnings = ['Kick evidence is a low-band attack/decay heuristic; bass stabs can resemble kicks.',
                'Phrase phase and musical layering need audition; no vocal or stem classification.']
    if intro_gap >= 4:
        warnings.append('The proposed intro contains a kick gap of at least one bar; avoid a blind linear low-EQ swap.')
    if not entries or not exits:
        warnings.append('No reliable straight 8/16-bar kick-supported window found on one side; review manually.')
    return {'version': VERSION, 'status': 'estimated', 'meter': '4/4 assumed',
            'drumsInOverride': drums_in, 'drumsInSource': 'human' if drums_in is not None else 'estimated',
            'bpm': round(float(bpm), 6), 'gridOffset': round(float(grid_offset), 6),
            'method': 'low-band transient attack + decay + grid support',
            'bars': bars, 'kicklessOpening': opening_kickless,
            'firstReliableKick': None if first_kick is None else round(grid_offset + first_kick * period, 4),
            'introMaxKicklessBeats': intro_gap, 'entryCandidates': entries, 'exitCandidates': exits,
            'musicalArrival':arrival,
            'strategy': 'choose_kick_supported_entry' if intro_gap >= 4 or opening_kickless else 'linear_swap_after_audition',
            'lowEqRule': 'Keep outgoing low end until incoming kick support is established; if that falls outside the overlap, choose another entry.',
            'warnings': warnings}
